from bddrest import status, response


def test_responseheader(app, httpreq):

    @app.route()
    def get(req):
        req.response.headers.add('x-foo', 'a', 'b')
        req.response.headers.add('x-foo', 'a', 'b')
        return 'index'

    with httpreq():
        assert status == 200
        assert response.headers['x-foo'] == 'a, b'
