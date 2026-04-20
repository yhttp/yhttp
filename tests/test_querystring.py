from bddrest import status, when, response, given


def test_querystring_encoding(app, httpreq):
    @app.route()
    def get(req):
        return ', '.join([f'{k}={v}' for k, v in req.query.items()])

    with httpreq(query='foo=bar baz'):
        assert response.text == 'foo=bar baz'

        when(query=given + dict(qux='thud quux'))
        assert response.text == 'foo=bar baz, qux=thud quux'


def test_querystring_none(app, httpreq):
    @app.route()
    def get(req, *, foo=None):
        bar = req.query.get('bar')
        return f'{foo if foo else "None"} {bar if bar else "None"}'

    with httpreq('/?foo=foo&bar=bar'):
        assert response.text == 'foo bar'

        when(query=given - 'foo')
        assert response.text == 'None bar'


def test_querystring(app, httpreq):

    @app.route()
    def get(req, *, baz='baz'):
        return f'{req.query["foo"]} ' \
            f'{baz if baz else "None"}'

    with httpreq('/?foo=bar&baz=qux'):
        assert status == 200
        assert response.text == 'bar qux'

        when(query=given - 'baz')
        assert status == 200
        assert response.text == 'bar baz'


def test_querystring_empty(app, httpreq):

    @app.route()
    def get(req, *, baz=None):
        assert req.query['baz'] == ''
        assert baz == ''

    with httpreq('/?baz'):
        assert status == 200

        when('/?baz=')
        assert status == 200


def test_querystring_duplicatefields(app, httpreq):

    @app.route()
    def post(req, *, foo=None):
        assert foo == 'baz'
        return ', '.join(req.query.getall('foo'))

    with httpreq(
            verb='post',
            query='foo=bar&foo=baz',
    ):
        assert status == 200
        assert response.text == 'bar, baz'


def test_querystring_malformed(app, httpreq):

    @app.route()
    def get(req, *, foo=None):
        return ', '.join(req.query.getall('foo'))

    with httpreq(rawurl='/?baz'):
        assert status == 400
