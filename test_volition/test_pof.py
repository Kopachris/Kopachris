from volition import pof as pof

f = open("Fighter2T-02.pof", 'rb')
print("Reading file...")
herc = pof.read_pof(f)
f.close()
print("Done!")

for chunk in herc:
    if chunk.CHUNK_ID == b'TXTR':
        txtr_chunk = chunk
    elif chunk.CHUNK_ID == b'HDR2':
        hdr_chunk = chunk
    elif chunk.CHUNK_ID == b'OBJ2':
        obj_chunk = chunk
        break

m = obj_chunk.get_mesh()
obj_chunk.set_mesh(m)

herc_min = [txtr_chunk, hdr_chunk, obj_chunk]

of = open("Herc.pof", 'wb')
print("Writing file...")
of.write(pof.write_pof(herc_min))
of.close()
print("Done!")