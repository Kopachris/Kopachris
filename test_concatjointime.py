def concat_str():
    x = "1000"
    for i in range(100):
        x += str(i)

def join_str():
    x = ["1000"]
    for i in range(100):
        x.append(str(i))
    y = "".join(x)

if __name__ == '__main__':
    import timeit
    print(timeit.timeit("concat_str()", setup="from __main__ import concat_str", number=100))
    print(timeit.timeit("join_str()", setup="from __main__ import join_str", number=100))
