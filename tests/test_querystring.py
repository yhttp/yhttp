from bddrest import status


def test_querystring(app, story, when):

    @app.route()
    def get(req, resp, *, baz=None):
        assert req.query['foo'] == 'bar'
        assert baz == 'qux'

    with story(app, '/?foo=bar&baz=qux'):
        assert status == 200

