from bddrest import status


def test_request(app, httpreq):
    @app.route('/foo')
    def get(req):
        assert req.fullpath == '/foo?bar=baz'
        assert req.scheme == 'http'
        assert req.headers.get('foo-bar') == 'baz'
        assert req.contenttype is None
        assert req.language == 'fa'

    with httpreq('/foo?bar=baz', headers={
        'Foo-Bar': 'baz',
        'Accept-Languages': 'fa-IR'
    }):
        assert status == 200
