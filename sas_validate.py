#!/usr/bin/env python3

"""Generate secure-enhanced ticket validation numbers according to IGT's
Slot Accounting System protocol.
"""

def crc(b, seed=0):
    for x in b:
        q = (seed ^ x) & 0o17
        seed = (seed >> 4) ^ (q * 0o10201)
        q = (seed ^ (x >> 4)) & 0o17
        seed = (seed >> 4) ^ (q * 0o10201)
    return (seed).to_bytes(2, byteorder='little')


def validate(v_id, v_seq):
    """Generate a validation number from seed values"""
    
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
    
    c = crc(b[:2])
    c += crc(b[2:4])
    c += crc(b[4:])
    
    n = [0, 0]
    
    for i, v in enumerate(c[3:]):
        n[0] += v << (i * 8)
        
    for i, v in enumerate(c[:3]):
        n[1] += v << (i * 8)
        
    v = [int(x) for x in '%08i%08i' % tuple(n)]
    v.reverse()
    v[7] |= (sum(v[:8]) % 5) << 1
    v[15] |= (sum(v[8:]) % 5) << 1
    v.reverse()
    
    return '00' + ''.join([str(x) for x in v])
    
    
def search(v_num, v_id=None, v_seq=None):
    """Brute-force search for a validation ID or sequence number given
    the other and a validation number.
    """
    
    if v_id is not None:
        print("Working with validation ID %i..." % v_id)
        for i in range(1<<24):
            v = validate(v_id, i)
            if v == v_num:
                print("Found %i with ID %i and sequence %i" % (v_num, v_id, i))
                return (v_id, i)
    elif v_seq is not None:
        print("Working with validation sequence %i..." % v_seq)
        for i in range(1<<24):
            v = validate(i, v_seq)
            if v == v_num:
                print("Found %i with ID %i and sequence %i" % (v_num, i, v_seq))
                return (i, v_seq)
    else:
        raise ValueError("Must have either validation ID or sequence")
    
    print("Not found")
    return False

    
if __name__ == '__main__':
    v_num = input("Validation number? ")
    v_id = input("Validation ID? ")
    v_id = int(v_id) if v_id else None
    v_seq = input("Validation sequence? ")
    v_seq = int(v_seq) if v_seq else None
    search(v_num, v_id, v_seq)
