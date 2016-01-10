from datetime import datetime
import threading
import time

def looper(i):
    begin_time = datetime.now()
    for i in range(i):
        pass
    end_time = datetime.now()

    d_time = end_time - begin_time
    ms = d_time.seconds * 1000
    ms += d_time.microseconds / 1000
    thread_name = threading.currentThread().getName()
    time.sleep(1)
    print(thread_name, " Time: ", ms, "ms")

num_threads = int(input('Num threads? '))
threads = list()

for i in range(num_threads):
    loop_count = int(input('Num to loop to? '))
    t = threading.Thread(target=looper, args=(loop_count,))
    threads.append(t)

print("Starting threads...")
for t in threads:
    t.start()
print("Threads running...")
