from bddrest import status, when, response

from yhttp.core.statuses import nocontent, ok, created, HTTPStatus


def test_status(app, httpreq):

    @app.route()
    @created()
    def post(req):
        return b''

    @app.route()
    @HTTPStatus(205, 'Reset Content')
    def put(req):
        return b''

    @app.route()
    @nocontent()
    def delete(req):
        return b''

    @app.route()
    @ok()
    def get(req):
        return b''

    with httpreq(verb='POST'):
        assert status == '201 Created'

        when(verb='PUT')
        assert status == 205

        when(verb='DELETE')
        assert status == 204
        assert response == ''

        when(verb='GET')
        assert status == 200
