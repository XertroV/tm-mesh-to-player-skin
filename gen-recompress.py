

@click.command()
@click.argument('gbx_file')
def gen_decompressed(gbx_file):
    out_file = gbx_file.split('.')[0] + "_recompress.Mesh.Gbx"
    uncompressed_file = gbx_file.split('/')[-1] + "_decompressed.bin"
    print(f"writing file {out_file} and uncompressed: {uncompressed_file}")

    item = Gbx(gbx_file)
    data = item.data
    # item_reader = item.find_raw_chunk_id(MESH_CHUNK_ID)
    # start_pos = item_reader.pos
    if True: # item_reader.read_uint32() == MESH_CHUNK_ID:
        mesh_data = data[:]
        # n_chunks = relevant_data.count(b"\x01\xde\xca\xfa")
        # print('n ends of chunks: ', n_chunks)
        # third_last_chunk_end = find_nth_pos(relevant_data, END_OF_A_CHUNK, n_chunks - 3) + 4
        # mesh_data = relevant_data[:third_last_chunk_end]
        # actual files seem to have extra stuff here
        # mesh_data = mesh_data[:8] + bytes('\x03\x00\x00\x00', encoding='UTF8') + mesh_data[8:]
        print(mesh_data[:12])


        print(len(mesh_data))
        print(mesh_data[:64].hex())
        print(mesh_data[-16:].hex())

        with open(uncompressed_file, 'bw') as f:
            f.write(mesh_data)
        compressed = lzo.compress(bytes(mesh_data), 9, False)
        c_len = len(compressed)
        d_len = len(mesh_data)
        c_len_le = struct.pack('<I', c_len).hex()
        d_len_le = struct.pack('<I', d_len).hex()
        print(d_len, d_len_le, c_len, c_len_le)

        print(compressed[:64].hex())
        print(compressed[-16:].hex())

        gbx_hex=f"47425806004255435200B00B09100000000100000000B00B0904000000050000000700000000000000{d_len_le}{c_len_le}"
        with open(out_file, 'bw') as f:
            f.write(binascii.unhexlify(gbx_hex))
            f.write(compressed)
