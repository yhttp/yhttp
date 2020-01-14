from yhttp.headerset import HeaderSet


def test_headerset():
    headers = HeaderSet()

    headers.add('Foo: foo value')
    assert headers['Foo'] == 'foo value'
    assert headers['foo'] == 'foo value'

    headers.add('Bar', 'bar 1nd', 'bar 2nd')
    assert headers['bar'] == 'bar 1nd; bar 2nd'

    headers['Baz'] = 'baz value'
    assert headers['baz'] == 'baz value'

    del headers['baz']
    assert len(headers) == 2

    assert str(headers) == '''foo: foo value\r\nbar: bar 1nd; bar 2nd'''

    headers += [
        ('qux', 'quux'),
        'quuz: corge'
    ]
    assert headers['qux'] == 'quux'
    assert headers['quuz'] == 'corge'

    headers = HeaderSet(['foo: bar', ('baz', 'qux')])
    assert headers['foo'] == 'bar'
    assert headers['baz'] == 'qux'

