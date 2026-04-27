from bddrest import status


def test_request(app, httpreq):
    @app.route('/foo')
    def get(req):
        assert req.fullpath == '/foo?bar=baz'
        assert req.scheme == 'http'
        assert req.headers.get('foo-bar') == 'baz'
        assert req.contenttype is None

    with httpreq('/foo?bar=baz', headers={'Foo-Bar': 'baz'}):
        assert status == 200
