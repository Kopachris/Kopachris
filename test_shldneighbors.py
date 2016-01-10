from datetime import datetime

begin_time = datetime.now()
a = 5
thing = list()
for i in range(80):
    thing.append(list())
    for j in range(3):
        for k in range(2):
            if a != 1:
                thing[i].append(a)
end_time = datetime.now()

d_time = end_time - begin_time
ms = d_time.seconds * 1000
ms += d_time.microseconds / 1000
print("Time: ", ms, "ms")
