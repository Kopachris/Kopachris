from datetime import datetime

begin_time = datetime.now()
for i in range(100000000):
    pass
end_time = datetime.now()

d_time = end_time - begin_time
ms = d_time.seconds * 1000
ms += d_time.microseconds / 1000
print("Time: ", ms, "ms")
