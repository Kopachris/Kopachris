#!/usr/bin/env python3

def bigEndian(s):
    """Takes a list of length-2 strings"""
    return littleEndian(s[-1::-1])
        
def littleEndian(s):
    l = len(s)
    result = 0
    for i, x in enumerate(s):
        result += int(x, 16) * (256 ** i)
    return result

def splitCount(s, count):
    return [''.join(x) for x in zip(*[list(s[z::count]) for z in range(count)])]

s = input("? ")
bytewise = splitCount(s.replace(' ', ''), 2)
groupwise = [splitCount(g, 2) for g in s.split()]

bytes_as_ints = [int(i, 16) for i in bytewise]
big_endian_groups = [bigEndian(g) for g in groupwise]
little_endian_groups = [littleEndian(g) for g in groupwise]

f = open('hex.txt', 'w')
f.write('Bytes\n')
for i in bytes_as_ints:
    f.write(str(i) + '\n')
f.write('\nBig endian\n')
for i in big_endian_groups:
    f.write(str(i) + '\n')
f.write('\nLittle endian\n')
for i in little_endian_groups:
    f.write(str(i) + '\n')

#print(bytes_as_ints)
#print(big_endian_groups)
#print(little_endian_groups)
#input()