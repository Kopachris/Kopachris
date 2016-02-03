#!/usr/bin/env python3

def crc(b, seed=0):
    for x in b:
        q = (seed ^ x) & 0o17
        seed = (seed >> 4) ^ (q * 0o10201)
        q = (seed ^ (x >> 4)) & 0o17
        seed = (seed >> 4) ^ (q * 0o10201)
    return seed


def validate(v_id, v_seq):
    if 0 > v_id >= 2**24:
        raise ValueError("Validation ID too large, %i" % v_id)
    if 0 > v_seq >= 2**24:
        raise ValueError("Validation sequence too large, %i" % v_seq)
    
    a = [x for x in (v_seq).to_bytes(3, byteorder='little')]
    a += [x for x in (v_id).to_bytes(3, byteorder='little')]
    
    b = [0] * 6
    b[5] = a[5] ^ a[1]
    b[4] = a[4] ^ a[0]
    b[3] = a[3] ^ a[1]
    b[2] = a[2] ^ a[0]
    b[1] = a[1]
    b[0] = a[0]
    
    
