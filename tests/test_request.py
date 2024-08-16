from bddrest import status


def test_request(app, Given):
    @app.route('/foo')
    def get(req):
        assert req.fullpath == 'http://bddrest-interceptor/foo?bar=baz'
        assert req.scheme == 'http'
        assert req.headers.get('foo-bar') == 'baz'
        assert req.contenttype is None

    with Given('/foo?bar=baz', headers={'Foo-Bar': 'baz'}):
        assert status == 200
