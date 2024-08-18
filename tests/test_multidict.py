
from yhttp.core.multidict import MultiDict


def test_multidict():
    d = MultiDict(backend=dict(foo=[1, 11]), bar=2)

    assert d.dict == dict(foo=[1, 11], bar=[2])
    assert len(d) == 2

    iterator = iter(d)
    assert next(iterator) == 'foo'
    assert next(iterator) == 'bar'

    assert 'foo' in d
    assert 'bar' in d
    del d['bar']
    assert 'bar' not in d

    assert ['foo'] == list(d.keys())

    assert d['foo'] == 11
    assert d.get('foo') == 11
    assert d.get('foo', None, 1) == 11
    assert d.get('foo', None, 0) == 1
    assert d.get('bar', None, 0) is None

    d['foo'] = 111
    assert d.getall('foo') == [1, 11, 111]

    d.replace('foo', 1)
    assert d.getall('foo') == [1]

    iterator = d.iterallitems()
    assert next(iterator) == ('foo', 1)
