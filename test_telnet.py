#!/usr/bin/env python3
 
from telnetlib import Telnet
import termutils as t
# ^custom module for platform-agnostic wipe/get_key functions
import sys
from multiprocessing import Process, Pipe
 
HOST = 'youras400host'
PORT = 23
 
sys.ps1 = ""
sys.ps2 = ""
 
# basic telnet client without keystroke buffering
 
def tn_loop(key_pipe):
    tn = Telnet(HOST, PORT)
    tn.write(b'\n')
    while True:
        if key_pipe.poll():
            tn.write(key_pipe.recv())
        data = tn.read_very_eager()
        print(data.decode(), end='')
   
 
if __name__ == '__main__':
    t.wipe()
   
    p_pipe, ch_pipe = Pipe()
    tn_conn = Process(target=tn_loop, args=(ch_pipe,))
    tn_conn.start()
   
    while True:
        try:
            k = t.get_key()
        except:
            sys.exit()
        else:
            p_pipe.send(k)