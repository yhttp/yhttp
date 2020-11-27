from bddrest import status, when, response, given


def test_querystring(app, Given):

    @app.route()
    def get(req, *, baz=None):
        return f'{req.query.get("foo")} {baz}'

    with Given('/?foo=bar&baz=qux'):
        assert status == 200
        assert response.text == 'bar qux'

        when(query=given - 'baz')
        assert status == 200
        assert response.text == 'bar None'
