from bddrest import status, when

from yhttp import statuscode


def test_status(app, Given):

    @app.route()
    @statuscode('201 Created')
    def post(req):
        return b''

    @app.route()
    @statuscode('205 Reset Content')
    def put(req):
        return b''

    with Given(verb='POST'):
        assert status == '201 Created'

        when(verb='PUT')
        assert status == 205
