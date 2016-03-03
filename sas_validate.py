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


def reverse_validate(v_num):
    """Attempt to reverse the validation algorithm to find validation ID and
    sequence, given a validation number. Validation number must start with '00'
    and be 18 digits long to be recognized as a secure-enhanced validation
    number.
    """
    
    if len(v_num) != 18 or not v_num.startswith('00'):
        raise ValueError("Not a valid secure-enhanced validation number")
        
    v = [int(x) for x in v_num[2:]]
    v.reverse()
    
    # find original v[7]
    found = 0
    x = 0
    for i in range(10):
        if (i | ((sum(v[:7]) + i) % 5) << 1) == v[7]:
            found += 1
            x = i
    if found > 1:
        raise Exception("Found too many values for original v[7]")
    elif not found:
        raise Exception("Couldn't find original v[7]")
    else:
        v[7] = x
        
    # find original v[15]
    found = 0
    x = 0
    for i in range(10):
        if (i | ((sum(v[8:15]) + i) % 5) << 1) == v[15]:
            found += 1
            x = i
    if found > 1:
        raise Exception("Found too many values for original v[15]")
    elif not found:
        raise Exception("Couldn't find original v[15]")
    else:
        v[15] = x
    
    v.reverse()
    
    n = [0,0]
    # convert digits to single integer
    n[0] = sum([x * 10**i for i, x in zip(range(7,-1,-1), v[:8])])
    n[1] = sum([x * 10**i for i, x in zip(range(7,-1,-1), v[8:])])
    
    # convert to bytes
    c = (n[1]).to_bytes(3, byteorder='little')
    c += (n[0]).to_bytes(3, byteorder='little')
    
    # brute-force original values for CRC
    b = [0] * 6
    founda = 0
    foundb = 0
    foundc = 0
    for x in range(256):
        for y in range(256):
            r = crc([x, y])
            if r == c[:2]:
                founda += 1
                b[:2] = [x, y]
            if r == c[2:4]:
                foundb += 1
                b[2:4] = [x, y]
            if r == c[4:]:
                foundc += 1
                b[4:] = [x, y]
    for f in (founda, foundb, foundc):
        if f > 1:
            raise Exception("Found CRC collision")
        elif not f:
            raise Exception("No match found for CRC")
    
    # reverse original XORing
    a = [0] * 6
    a[0] = b[0]
    a[1] = b[1]
    a[2] = b[2] ^ b[0]
    a[3] = b[3] ^ b[1]
    a[4] = b[4] ^ b[0]
    a[5] = b[5] ^ b[1]
    
    # convert back to integers!
    n = [0,0]
    for i, x in enumerate(a[:3]):
        # validation sequence
        n[1] += x << (i * 8)
    for i, x in enumerate(a[3:]):
        # validation ID
        n[0] += x << (i * 8)
        
    return tuple(n)

    
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
