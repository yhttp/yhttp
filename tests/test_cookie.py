from http import cookies

from bddrest import status, response


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
            domain='example.com'
        )

    headers = {'Cookie': 'counter=1;'}
    with Given(headers=headers):
        assert status == 200
        assert 'Set-cookie' in response.headers
        assert response.headers['Set-cookie'] == \
            'counter=2; Domain=example.com; Max-Age=1; Path=/a'

        cookie = cookies.SimpleCookie(response.headers['Set-cookie'])
        counter = cookie['counter']
        assert counter.value == '2'
        assert counter['path'] == '/a'
        assert counter['domain'] == 'example.com'
        assert counter['max-age'] == '1'
