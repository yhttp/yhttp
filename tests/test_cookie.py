
from http import cookies

from bddrest import status, response


def test_cookie(app, session):
    @app.route()
    def get():
        counter = app.request.cookies['counter']
        app.request.cookies['counter'] = str(int(counter.value) + 1)
        app.request.cookies['counter']['max-age'] = 1
        app.request.cookies['counter']['path'] = '/a'
        app.request.cookies['counter']['domain'] = 'example.com'

    headers = {'Cookie': 'counter=1;'}
    with session(app, headers=headers):
        assert status == 200
        assert 'Set-cookie' in response.headers

        cookie = cookies.SimpleCookie(response.headers['Set-cookie'])
        counter = cookie['counter']
        assert counter.value == '2'
        assert counter['path'] == '/a'
        assert counter['domain'] == 'example.com'
        assert counter['max-age'] == '1'

