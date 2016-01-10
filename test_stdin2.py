import sys
import os
from multiprocessing import Process, Pipe
import time

def _win_getkey():
    import msvcrt
    if msvcrt.kbhit():
        return msvcrt.getch()

def _nix_getkey():
    import select
    import termios
    import tty
    
    def is_data():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
    
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        if is_data():
            k = sys.stdin.read(1)
        else:
            k = None
    except:
        k = None
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return k

if os.name == 'nt':
    getkey = _win_getkey
else:
    getkey = _nix_getkey

def key_loop(p):
    while True:
        k = getkey()
        if k is not None:
            p.send(k)
    
if __name__ == '__main__':
    p_pipe, ch_pipe = Pipe()
    key_listener = Process(target=key_loop, args=(ch_pipe,))
    key_listener.start()
    
    last_time = time.time()
    while True:
        if time.time() - last_time >= 1:
            print('.', end='')
            last_time = time.time()
        
        if p_pipe.poll():
            print('\ninput: ' + repr(p_pipe.recv()))
            