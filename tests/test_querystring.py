from bddrest import status, when, response, given


def test_querystring_none(app, Given):
    @app.route()
    def get(req, *, foo=None):
        bar = req.query.get('bar')
        return f'{foo[0] if foo else "None"} {bar[0] if bar else "None"}'

    with Given('/?foo=foo&bar=bar'):
        assert response.text == 'foo bar'

        when(query=given - 'foo')
        assert response.text == 'None bar'


# TODO: test duplicate fields in both kwargsonly and req.query
def test_querystring(app, Given):

    @app.route()
    def get(req, *, baz=None):
        return f'{','.join(req.query["foo"])} ' \
            f'{','.join(baz) if baz else "None"}'

    with Given('/?foo=bar&baz=qux'):
        assert status == 200
        assert response.text == 'bar qux'

        when(query=given - 'baz')
        assert status == 200
        assert response.text == 'bar None'


def test_querystring_empty(app, Given):

    @app.route()
    def get(req, *, baz=None):
        assert req.query.get('baz') is None
        assert baz is None

    with Given('/?baz='):
        assert status == 200
