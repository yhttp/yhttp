from bddrest import status

from yhttp.core import statuses


def test_httpstatus(app, httpreq):
    def _handler(req, exc, debug):
        if exc.code != 400:
            return False

        statuses.notfound().setupresponse(req.response)
        return True

    app.statushandler = _handler

    @app.route()
    def get(req):
        raise statuses.badrequest()

    with httpreq():
        assert status == 404
