#!/usr/bin/env python3
from pathlib import Path
import struct
import binascii

import click

from pygbx import Gbx
import lzo

@click.command()
@click.argument('gbx_file')
@click.option('--suffix', help="apply a suffix to the output file", default="_recompressed")
def gen_decompressed(gbx_file, suffix):
    gbx_file_p = Path(gbx_file)
    ext = '.'.join(gbx_file_p.name.split('.')[-2:])
    fname = '.'.join(gbx_file_p.name.split('.')[:-2])
    out_file = f"{fname}{suffix}.{ext}"
    print(f"writing recompressed file: {out_file}")

    with open(gbx_file_p, 'br') as f:
        orig_gbx = f.read()

    gbx_header_parts = [orig_gbx[:13]] # GBXvvBUCRxxxx
    user_data_len = struct.unpack('<I', orig_gbx[13:17])[0]
    gbx_header_parts.append(orig_gbx[13:(13+4+user_data_len+8)]) # also get node count + external node count
    if gbx_header_parts[-1][-4:] != b'\x00'*4:
        raise Exception('External nodes unsupported (requires extra implementation; see https://wiki.xaseco.org/wiki/GBX#Reference_table)')
    # next 2 uint32s are sizes, so we don't need them.
    header = b''.join(gbx_header_parts)

    item = Gbx(gbx_file)
    data = item.data
    # with open(uncompressed_file, 'bw') as f:
    #     f.write(mesh_data)
    compressed = lzo.compress(bytes(data), 9, False)
    c_len = len(compressed)
    d_len = len(data)
    c_len_le = struct.pack('<I', c_len).hex()
    d_len_le = struct.pack('<I', d_len).hex()
    print(d_len, d_len_le, c_len, c_len_le)

    print(compressed[:64].hex())
    print(compressed[-16:].hex())

    lengths = binascii.unhexlify(f"{d_len_le}{c_len_le}")

    with open(out_file, 'bw') as f:
        f.write(header)
        f.write(lengths)
        f.write(compressed)

if __name__ == "__main__":
    gen_decompressed()
