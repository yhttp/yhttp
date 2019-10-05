from bddrest import status


def test_querystring(app, session, when):

    @app.route()
    def get(*, baz=None):
        assert app.request.query['foo'] == 'bar'
        assert baz == 'qux'

    with session(app, '/?foo=bar&baz=qux'):
        assert status == 200

