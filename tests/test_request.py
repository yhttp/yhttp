from bddrest import status


def test_request(app, session, when):
    @app.route('/foo')
    def get():
        assert app.request.fullpath == 'http://bddrest-interceptor/foo?bar=baz'
        assert app.request.scheme == 'http'

    with session(app, '/foo?bar=baz'):
        assert status == 200


