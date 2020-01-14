from bddrest import status, response


def test_responseheader(app, story):

    @app.route()
    def get(req, resp):
        resp.headers.add('x-foo', 'a', 'b')
        return 'index'

    with story(app):
        assert status == 200
        assert response.headers['x-foo'] == 'a; b'

