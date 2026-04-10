from yhttp.core.cookieset import CookieSet


def test_cookieset():
    cookies = CookieSet()

    cookies['foo'] = 'Foo'
    cookies['bar'] = 'Bar'

    assert cookies.tolist() == [
        ('Set-Cookie', 'bar=Bar'),
        ('Set-Cookie', 'foo=Foo'),
    ]
