def l():
    a = list()
    for i in range(1000):
        a.append(i)
    b = set(a)

def s():
    a = set()
    for i in range(1000):
        a.add(i)
    b = list(a)

if __name__ == '__main__':
    from timeit import timeit
    print(timeit("l()", setup="from __main__ import l", number=100000))
    print(timeit("s()", setup="from __main__ import s", number=100000))
