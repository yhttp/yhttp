from bddrest import status


def test_request(app, story, when):
    @app.route('/foo')
    def get(req):
        assert req.fullpath == 'http://bddrest-interceptor/foo?bar=baz'
        assert req.scheme == 'http'
        assert req.headers.get('foo') == 'bar'

    with story(app, '/foo?bar=baz', headers=dict(foo='bar')):
        assert status == 200


