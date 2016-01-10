import sys
#import threading
import time
#import queue
from multiprocessing import Process, Pipe

def add_input(input_pipe):
    while True:
        input_pipe.send(sys.stdin.read(1))

def foobar():
    p_pipe, ch_pipe = Pipe()
    input_thread = Process(target=add_input, args=(ch_pipe,))
    input_thread.start()

    #input_thread = threading.Thread(target=add_input, args=(input_queue,))
    #input_thread.daemon = True
    #input_thread.start()

    last_update = time.time()
    while True:

        if time.time()-last_update>0.5:
            print(".", end='')
            last_update = time.time()

        if p_pipe.poll(1):
            print("\ninput:" + p_pipe.recv())

if __name__ == '__main__':
    foobar()