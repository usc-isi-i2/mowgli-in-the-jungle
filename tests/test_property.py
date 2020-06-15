import abc


class ParentClass(abc.ABC):
    def __init__(self, p):
        self._myproperty = p

    @property
    @abc.abstractmethod
    def myproperty(self):
        return self._myproperty

    @myproperty.setter
    def myproperty(self, p):
        self._myproperty = p


class TestClass(ParentClass):
    def __init__(self, p=-1):
        super().__init__(p)

    @property
    def myproperty(self):
        print(f'myproperty setter {self._myproperty}')
        return self._myproperty

    @myproperty.setter
    def myproperty(self, p):
        print(f'myproperty getter {p}')
        self._myproperty = p


class SecondTestClass:
    def __init__(self):
        self._test_class = None

    @property
    def test_class(self):
        print('test_class getter')
        return self._test_class

    @test_class.setter
    def test_class(self, c):
        print('test_class setter')
        self._test_class = c


# o = TestClass(20)
# print('object initialized')
# print(o.myproperty)
# o.myproperty = 30
# print(o.myproperty)

o = TestClass(20)
so = SecondTestClass()
print('object initialized')
so.test_class = o
print(f'A pause')
so.test_class.myproperty = o.myproperty + 20
