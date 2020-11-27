from bddrest import status


def test_request(app, Given):
    @app.route('/foo')
    def get(req):
        assert req.fullpath == 'http://bddrest-interceptor/foo?bar=baz'
        assert req.scheme == 'http'
        assert req.headers.get('foo') == 'bar'

    with Given('/foo?bar=baz', headers=dict(foo='bar')):
        assert status == 200
