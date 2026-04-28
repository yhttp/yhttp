from bddrest import status, response

from yhttp.core import statuses


def test_middleware_returnnone(app, httpreq):
    def middleware(request):
        request.query['baz'] = 'qux'

    app.request_middlewares.append(middleware)

    @app.route()
    def get(req):
        return '&'.join([f'{k}={v}' for k, v in req.query.items()])

    with httpreq('?foo=bar'):
        assert status == 200
        assert response.text == 'foo=bar&baz=qux'


def test_middleware_returnbody(app, httpreq):
    def middleware(request):
        return 'something else'

    app.request_middlewares.append(middleware)

    @app.route()
    def get(req):
        return 'foobar'

    with httpreq('?foo=bar'):
        assert status == 200
        assert response.text == 'something else'


def test_middleware_raise(app, httpreq):
    def middleware(request):
        raise statuses.found('/foo')

    app.request_middlewares.append(middleware)

    @app.route()
    def get(req):
        return 'foobar'

    with httpreq('?foo=bar'):
        assert status == 302
        assert response.headers['location'] == '/foo'
