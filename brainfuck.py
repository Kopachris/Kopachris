"""brainfuck.py - a simply Brainfuck interpreter

Brainfuck has an instruction pointer and a data pointer.
The instruction pointer is, effectively, the current
position in the source file.  The data pointer is the
current data cell in an arbitrarily large array.

The data pointed to by the data pointer can be operated
on by the following instructions:

> - increment data pointer (point to next cell)
< - decrement data pointer (point to prev cell)
+ - increment value at data pointer
- - decrement value at data pointer
. - output the byte at the data pointer
, - store one byte of input at the data pointer
[ - if the byte at the data pointer is zero, move the instruction
    pointer to the matching ] instruction
] - if the byte at the data pointer is nonzero, move the
    instruction pointer to the matching [ instruction
    
Using [ and ], a simple for loop:

for i in range(10):
    do_something()

can be constructed as such:

+++++ +++++            # initialize counter (cell 0) to 10
[
    > +++    #do something
    <        # decrement pointer back to cell 0
    -        # decrement counter
]

Module usage:

>>> import brainfuck as bf
>>> interp = bf.Interpreter()
>>> interp.parse(filename)    # given a path to a file
Hello world.
>>> interp.reset()
>>> f = open(filename)
>>> interp.parse(f)        # given a file object
Hello world.
>>> interp.reset()
>>> interp.parse(s)        # given a string that doesn't look like a file path
Hello world.
"""


class Interpreter:
    """A simple Brainfuck interpreter.  Can
    be subclassed to add instructions.
    """
    def __init__(self):
        self._valid_inst = {
            '>': self._inc_dptr,
            '<': self._dec_dptr,
            '+': self._inc_data,
            '-': self._dec_data,
            '.': self._out,
            ',': self._in,
            '[': self._bloop,
            ']': self._eloop,
            }
        self.reset()

    def reset(self):
        self._iptr = 0        # instruction pointer
        self._data = [0]    # all data cells
        self._dptr = 0        # data pointer
        self._max_data_value = 255    # one byte, as per reference impl
        self._min_data_value = 0
        
    def parse(self, s):
        try:
            s = s.read()
        except:        # not a file
            try:
                f = open(s)
                s = f.read()
                f.close()
            except:        # not a file path
                pass
        
        self._src = s
        while self._iptr < len(s):
            c = s[self._iptr]
            #print(c)
            if c in self._valid_inst:
                self._valid_inst[c]()
            #print("dptr {} data {}".format(self._dptr, self._data[self._dptr]))
            self._iptr += 1
                
    def _inc_dptr(self):
        self._dptr += 1
        if self._dptr >= len(self._data):
            self._data.append(0)
            
    def _dec_dptr(self):
        if self._dptr > 0:
            self._dptr -= 1
            
    def _inc_data(self):
        if self._data[self._dptr] < self._max_data_value:
            self._data[self._dptr] += 1
            
    def _dec_data(self):
        if self._data[self._dptr] > self._min_data_value:
            self._data[self._dptr] -= 1
            
    def _out(self):
        c = chr(self._data[self._dptr])
        print(c, end='')
        
    def _in(self):
        c = input('')[0]
        self._data[self._dptr] = ord(c)
        
    def _bloop(self):
        if not self._data[self._dptr]:
            #print(' Found bloop')
            self._find_eloop()
            
    def _eloop(self):
        if self._data[self._dptr]:
            #print(' Found eloop')
            self._find_bloop()
            
    def _find_eloop(self):
        n = 0    # nest counter
        i = self._iptr + 1
        for c in self._src[i:]:
            self._iptr += 1
            if c == '[':
                #print(' Found nest')
                n += 1
            elif c == ']' and n:
                #print(' Found end nest')
                n -= 1
            elif c == ']' and not n:
                #print(' Found end loop')
                break
                
    def _find_bloop(self):
        n = 0    # nest counter
        i = self._iptr
        for c in self._src[:i][::-1]:
            self._iptr -= 1
            if c == ']':
                #print(' Found nest')
                n += 1
            elif c == '[' and n:
                #print(' Found end nest')
                n -= 1
            elif c == '[' and not n:
                #print(' Found begin loop')
                self._iptr -= 1
                break

