# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

## Bintools module
## Copyright (c) 2012 by Christopher Koch

"""This module contains wrapper functions for struct.pack() and struct.unpack(), as well as a file-like RawData class useful for parsing binary data like a file without requiring a file to be open on the disk."""

## No guarantees about pep8 compliance

from struct import *

# Note for the pack() and unpack() wrappers:
# u = Unpacked data
# p = Packed data
# Mind your p's and u's

def unpack_byte(bin_data):
    """Wrapper function for struct.unpack().  Can accept an iterable of any length and will unpack the contents into a list of integers."""
    
    u = int()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 1:
        u = unpack('b', p)[0]
        
    elif len(p) > 1:
        u = list(unpack('{}b'.format(len(p)), p))
        
    return u
    
def unpack_ubyte(bin_data):
    
    # unsigned byte (numeric)
    
    u = int()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 1:
        u = unpack('B', p)[0]
        
    elif len(p) > 1:
        u = list(unpack('{}B'.format(len(p)), p))
        
    return u
    
def unpack_short(bin_data):

    # signed short
    
    u = int()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 2:
        u = unpack('h', p)[0]
        
    elif len(p) > 2 and (len(p) % 2) == 0:
        u = list(unpack('{}h'.format(len(p) / 2), p))
        
    return u
    
def unpack_ushort(bin_data):

    # unsigned short
    
    u = int()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 2:
        u = unpack('H',p)[0]
        
    elif len(p) > 2 and (len(p) % 2) == 0:
        u = list(unpack('{}H'.format(len(p) / 2), p))
        
    return u
    
def unpack_int(bin_data):

    # signed int32
    
    u = int()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 4:
        u = unpack('i', p)[0]
        
    elif len(p) > 4 and (len(p) % 4) == 0:
        u = list(unpack('{}i'.format(len(p) / 4), p))
        
    return u
    
def unpack_uint(bin_data):

    # unsigned int32
    
    u = int()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 4:
        u = unpack('I', p)[0]
        
    elif len(p) > 4 and (len(p) % 4) == 0:
        u = list(unpack('{}I'.format(len(p) / 4), p))
        
    return u
    
def unpack_float(bin_data):

    # float
    
    u = float()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 4:
        u = unpack('f', p)
        
    elif len(p) > 4 and (len(p) % 4) == 0:
        u = list(unpack('{}f'.format(len(p) / 4), p))
        
    return u
    
def unpack_vector(bin_data):

    # tuple of three floats
    
    u = tuple()
    try:
        p = bytes(bin_data)
    except TypeError:
        p = bytes(bin_data, "utf-8", "ignore")
    
    if len(p) == 12:
        u = unpack('3f', p)
        
    elif len(p) > 12 and (len(p) % 12) == 0:
        u = list()
        for i in range(len(p) / 12):
            u.append(unpack('3f', p[i * 12:i * 12 + 12]))
            
    return tuple(u)
    
def pack_byte(x):
    
    # signed byte
    
    p = bytes()
    try:
        u = tuple(x)
        p = pack('b', u[0])
        for i in u[1:]:
            p += pack('b', i)
    except TypeError:
        p = pack('b', x)
    
    return p
    
def pack_ubyte(x):

    # unsigned byte
    
    p = bytes()
    try:
        u = tuple(x)
        p = pack('B', u[0])
        for i in u[1:]:
            p += pack('b', i)
    except TypeError:
        p = pack('B', x)
        
    return p
            
def pack_short(x):

    # signed short
    
    p = bytes()
    try:
        u = tuple(x)
        p = pack('h', u[0])
        for i in u[1:]:
            p += pack('h', i)
    except TypeError:
        p = pack('h', x)
        
    return p
    
def pack_ushort(x):

    # unsigned short
    
    p = bytes()
    try:
        u = tuple(x)
        p = pack('H', u[0])
        for i in u[1:]:
            p += pack('H', i)
    except TypeError:
        p = pack('H', x)
        
    return p
    
def pack_int(x):

    # signed int32
    
    p = bytes()
    try:
        u = tuple(x)
        p = pack('i', u[0])
        for i in u[1:]:
            p += pack('i', i)
    except TypeError:
        p = pack('i', x)
        
    return p
    
def pack_uint(x):

    # unsigned int32
    
    p = bytes()
    try:
        u = tuple(x)
        p = pack('I', u[0])
        for i in u[1:]:
            p += pack('I', i)
    except TypeError:
        p = pack('I', x)
        
    return p
    
def pack_float(x):

    # float
    
    p = bytes()
    try:
        u = tuple(x)
        p = pack('f', u[0])
        for i in u[1:]:
            p += pack('f', i)
    except TypeError:
        p = pack('f', x)
        
    return p
    
def pack_string(x):

    # int with length of string followed by chars
    
    u = bytes(x)
    p = pack('i', len(u))
    p += u
    
    return p
    
class RawData:

    ## May be deprecated if we can use a Python file object faster

    """Creates an object that can be read like a file.  Takes any sequence of data as an argument.  May typically be used to pass only a part of a file to a function so that the part of the file can still be read like a file.
    
    Methods:
        read(length = 0) -- Returns a slice of data from the current address to the current address plus length.  Increases current address by length.  If length is 0 or not provided, returns the entire data.
        seek(new_addr[, whence = 0]) -- Changes the current address.  If whence is 0, new_addr is bytes from beginning; if whence is 1, new_addr is bytes from current address; if whence is 2, new_addr is bytes from end."""
    def __init__(self, data):
        self.data = data
        self.addr = 0
        
    def __len__(self):
        return len(self.data)
        
    def __repr__(self):
        return "<RawData object of length {} at index {}>".format(len(self.data), self.addr)
        
    def read(self, length = 0):
        if length == 0:
            return self.data
        else:
            out = self.data[self.addr:self.addr + length]
            self.addr += length
            return out
            
    def seek(self, new_addr, whence = 0):
        if whence == 1:
            self.addr += new_addr
        elif whence == 2:
            self.addr = len(self.data) - new_addr
        else:
            self.addr = new_addr