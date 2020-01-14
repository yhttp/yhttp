from bddrest import status


def test_request(app, story, when):
    @app.route('/foo')
    def get():
        assert app.request.fullpath == 'http://bddrest-interceptor/foo?bar=baz'
        assert app.request.scheme == 'http'

    with story(app, '/foo?bar=baz'):
        assert status == 200


