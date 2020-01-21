from bddrest import status, when


def test_querystring(app, Given):

    @app.route()
    def get(req, *, baz=None):
        assert req.query['foo'] == 'bar'
        assert baz == 'qux'

    with Given('/?foo=bar&baz=qux'):
        assert status == 200

