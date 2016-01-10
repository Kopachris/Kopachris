#!/usr/bin/env python3

import string

def splitCount(s, count):
     return [''.join(x) for x in zip(*[list(s[z::count]) for z in range(count)])]

encrypted_pass = input('Password to decrypt?')
encrypted_bytes = splitCount(encrypted_pass, 2)
encrypted_chars = [chr(int(c, 16)) for c in encrypted_bytes]
clear = ''

for c in encrypted_chars:
    if c.isalpha():
        c_idx = string.ascii_uppercase.index(c)
        clear += string.ascii_uppercase[25-c_idx]
    elif c.isdigit():
        clear += string.digits[9-int(c)]

print(clear[-1::-1])



