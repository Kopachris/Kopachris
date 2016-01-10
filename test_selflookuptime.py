#from copy import deepcopy

class A:
    def __init__(self, item):
        self.item = item
    def thing1(self):
        a = self.item
        b = "1"
        for i in range(3):
            a += b
        self.item = a
    def thing2(self):
        b = "1"
        for i in range(3):
            self.item += b

m = A("test")
n = A("test")

if __name__ == '__main__':
    import timeit
    print(timeit.timeit("m.thing1()", setup="from __main__ import m", number=10000))
    print(timeit.timeit("n.thing2()", setup="from __main__ import n", number=10000))
        
