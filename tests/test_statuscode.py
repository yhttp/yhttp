from bddrest import status, when, response

from yhttp.core import statuscode
from yhttp.core.statuses import nocontent, ok


def test_status(app, Given):

    @app.route()
    @statuscode('201 Created')
    def post(req):
        return b''

    @app.route()
    @statuscode('205 Reset Content')
    def put(req):
        return b''

    @app.route()
    @statuscode(nocontent)  # 204 No Content
    def delete(req):
        return b''

    @app.route()
    @statuscode(ok)
    def get(req):
        return b''

    with Given(verb='POST'):
        assert status == '201 Created'

        when(verb='PUT')
        assert status == 205

        when(verb='DELETE')
        assert status == 204
        assert response == ''

        when(verb='GET')
        assert status == 200
