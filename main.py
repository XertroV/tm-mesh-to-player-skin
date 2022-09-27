#!/usr/bin/env python3
from pathlib import Path
import struct
import binascii

import click

from pygbx import Gbx, GbxType
import lzo


def logr(f):
    def inner(*args):
        ret = f(*args)
        print(f"{f.__name__} returned {ret}")
        return ret
    return inner



@logr
def find_mesh(item_bin: bytes):
    return item_bin.find(b"\x00\xb0\x0b\x09")

MESH_CHUNK_ID = 0x090bb000
# END_OF_A_CHUNK = 0xfacade01
END_OF_A_CHUNK = b"\x01\xde\xca\xfa"

def find_nth_pos(data: bytearray, chunk: bytes, n=1):
    next_pos = data.find(chunk)
    if n <= 1: return next_pos
    return next_pos + 4 + find_nth_pos(data[next_pos+4:], chunk, n=n-1)

@click.command()
@click.argument('item_file')
@click.option('--suffix', help="apply a suffix to the output file", default="_ItemRip")
def conv_item(item_file, suffix):
    item_file_p = Path(item_file)
    # ext = '.'.join(item_file_p.name.split('.')[-2:])
    fname = '.'.join(item_file_p.name.split('.')[:-2])
    out_file = f"{fname}{suffix}.Mesh.Gbx"
    dump_file = f"{fname}_uncompressed.bin"

    print(f"writing mes rip out to {out_file}")

    item = Gbx(item_file)
    data = item.data
    item_reader = item.find_raw_chunk_id(MESH_CHUNK_ID)
    start_pos = item_reader.pos
    if item_reader.read_uint32() == MESH_CHUNK_ID:
        relevant_data = data[start_pos:]
        n_chunks = relevant_data.count(b"\x01\xde\xca\xfa")
        print('n ends of chunks: ', n_chunks)
        third_last_chunk_end = find_nth_pos(relevant_data, END_OF_A_CHUNK, n_chunks - 3) + 4
        mesh_data = relevant_data[:third_last_chunk_end]
        # actual files seem to have extra stuff here
        mesh_data = mesh_data[:8] + bytes('\x03\x00\x00\x00', encoding='UTF8') + mesh_data[8:]

        print(len(mesh_data))
        print(mesh_data[:64].hex())
        print(mesh_data[-16:].hex())

        # with open(uncompressed_file, 'bw') as f:
        #     f.write(mesh_data)
        compressed = lzo.compress(bytes(mesh_data), 9, False)
        c_len = len(compressed)
        d_len = len(mesh_data)
        c_len_le = struct.pack('<I', c_len).hex()
        d_len_le = struct.pack('<I', d_len).hex()
        print(d_len, d_len_le, c_len, c_len_le)

        print(compressed[:64].hex())
        print(compressed[-16:].hex())

        gbx_hex=f"47425806004255435200B00B09100000000100000000B00B0904000000050000000a00000000000000{d_len_le}{c_len_le}"
        with open(out_file, 'bw') as f:
            f.write(binascii.unhexlify(gbx_hex))
            f.write(compressed)

    # with open(i_bin)tem_file, 'rb') as f:
    #     item_bin = f.read()
    # print(f"Read item of length: {len(item_bin)}")
    # find_mesh(item


# hmm error with counts/ids of instances w/in the data structure -- node IDs maybe?


# node count in item is 4 more than mesh: 1 for collector ctn and 3 for wrappers around the mesh (implied by the extra 3 facade01's at the end)
# that's a guess


if __name__ == "__main__":
    conv_item()
