from bddrest import status, when, response, given


def test_querystring_encoding(app, Given):
    @app.route()
    def get(req):
        return ', '.join([f'{k}={v}' for k, v in req.query.items()])

    with Given(query='foo=bar baz'):
        assert response.text == 'foo=bar baz'

        when(query=given + dict(qux='thud quux'))
        assert response.text == 'foo=bar baz, qux=thud quux'


def test_querystring_none(app, Given):
    @app.route()
    def get(req, *, foo=None):
        bar = req.query.get('bar')
        return f'{foo if foo else "None"} {bar if bar else "None"}'

    with Given('/?foo=foo&bar=bar'):
        assert response.text == 'foo bar'

        when(query=given - 'foo')
        assert response.text == 'None bar'


def test_querystring(app, Given):

    @app.route()
    def get(req, *, baz=None):
        return f'{req.query["foo"]} ' \
            f'{baz if baz else "None"}'

    with Given('/?foo=bar&baz=qux'):
        assert status == 200
        assert response.text == 'bar qux'

        when(query=given - 'baz')
        assert status == 200
        assert response.text == 'bar None'


def test_querystring_empty(app, Given):

    @app.route()
    def get(req, *, baz=None):
        assert req.query['baz'] == ''
        assert baz == ''

    with Given('/?baz='):
        assert status == 200


def test_querystring_duplicatefields(app, Given):

    @app.route()
    def post(req, *, foo=None):
        assert foo == 'baz'
        return ', '.join(req.query.getall('foo'))

    with Given(
            verb='post',
            query='foo=bar&foo=baz',
    ):
        assert status == 200
        assert response.text == 'bar, baz'
