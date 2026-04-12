from bddrest import status, given, when, response

from yhttp.core import statuses


def test_httpstatus(app, httpreq):
    def _handler(req, exc, debug):
        # if isinstance(exc,
        statuses.notfound().setupresponse(req.response)
        return True

    app.statushandler = _handler

    @app.route()
    def get(req):
        raise statuses.badrequest()

    with httpreq():
        assert status == 404
