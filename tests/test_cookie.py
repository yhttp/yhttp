from bddrest import status, response, when

from yhttp.core import statuses


def test_cookie(app, Given):
    @app.route()
    def get(req):
        resp = req.response
        counter = req.cookies.get('counter')
        resp.setcookie(
            'counter',
            str(int(counter.value) + 1),
            maxage=1,
            path='/a',
            domain='example.com',
            comment='Lorem ipsum',
            httponly=True,
            samesite='Lax',
            expires='Thu, 01 Jan 2030 00:00:00 GMT',
        )
        if 'foo' not in req.cookies:
            resp.setcookie(
                'foo',
                'bar',
            )

    cookie = {'counter': '1;'}
    with Given(cookies=cookie):
        assert status == 200
        assert 'counter' in response.cookies
        assert 'foo' in response.cookies
        assert response.cookies['counter'] == \
            '2; Comment="Lorem ipsum"; Domain=example.com; ' \
            'expires=Thu, 01 Jan 2030 00:00:00 GMT; HttpOnly; Max-Age=1; ' \
            'Path=/a; SameSite=Lax'
        assert response.cookies['foo'] == 'bar'

        when(cookies=dict(
            counter=response.cookies['counter'],
            foo=response.cookies['foo']
        ))
        assert response.cookies['counter'] == \
            '3; Comment="Lorem ipsum"; Domain=example.com; ' \
            'expires=Thu, 01 Jan 2030 00:00:00 GMT; HttpOnly; Max-Age=1; ' \
            'Path=/a; SameSite=Lax'
        assert 'foo' not in response.cookies


def test_secure_cookie(app, Given):
    @app.route()
    def get(req):
        resp = req.response
        try:
            resp.setcookie(
                'foo',
                'bar',
                secure=True
            )
        except AssertionError:
            raise statuses.forbidden()

    with Given():
        assert status == 403

        when(https=True)
        assert status == 200
        assert response.cookies['foo'] == 'bar; Secure'
