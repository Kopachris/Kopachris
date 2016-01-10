class A:
    def __init__(self, foo):
        self.__foo = foo

    def bar(self, baz):
        foo = self.__foo
        self.baz(baz)
        print(foo)

    def baz(self, bang):
        foo = self.__foo
        foo = bang
        self.__foo = foo

    def spam(self):
        print(self.__foo)


a = A('green eggs')
a.bar('ham')
a.spam()
