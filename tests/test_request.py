from bddrest import status


def test_request(app, story, when):
    @app.route('/foo')
    def get(req):
        assert req.fullpath == 'http://bddrest-interceptor/foo?bar=baz'
        assert req.scheme == 'http'

    with story(app, '/foo?bar=baz'):
        assert status == 200


