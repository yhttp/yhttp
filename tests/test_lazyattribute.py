from yhttp.core.lazyattribute import lazyattribute


def test_lazyattribute():
    class Foo:
        counter = 0

        @lazyattribute
        def bar(self):
            self.counter += 1
            return self.counter

    foo = Foo()
    assert foo.bar == 1
    assert foo.bar == 1
    assert foo.bar == 1

    assert callable(Foo.bar)
    assert Foo.bar.__name__ == 'bar'
