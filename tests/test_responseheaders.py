from bddrest import status, response


def test_responseheader(app, Given):

    @app.route()
    def get(req):
        req.response.headers.add('x-foo', 'a', 'b')
        return 'index'

    with Given():
        assert status == 200
        assert response.headers['x-foo'] == 'a; b'
