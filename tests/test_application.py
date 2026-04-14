from datetime import datetime

from bddrest import status, response, when

import yhttp.core as y


def test_pipeline(app, httpreq):
    configurecalled = None
    readycalled = None
    endresponsecalled = 0

    @app.when
    def configure(resp):
        nonlocal configurecalled
        configurecalled = datetime.now()

    @app.when
    def ready(resp):
        nonlocal readycalled
        readycalled = datetime.now()

    @app.when
    def startresponse(resp):
        resp.headers.add('x-qux', 'quux')

    @app.when
    def endresponse(resp):
        nonlocal endresponsecalled
        endresponsecalled += 1

    @app.route('/foos')
    def get(req):
        assert req is not None
        assert req.response is not None
        return 'foo1, foo2, foo3'

    @app.route()
    def get(req):  # noqa: W0404
        req.response.headers.add('x-foo', 'a', 'b')
        return 'index'

    @app.route()
    def post(req):
        return

    app.ready()
    assert configurecalled
    assert readycalled
    assert configurecalled < readycalled

    with httpreq():
        assert status == 200
        assert response == 'index'
        assert 'content-type' not in response.headers
        assert 'x-foo' in response.headers
        assert response.headers['x-qux'] == 'quux'
        assert endresponsecalled == 1

        when('/foos')
        assert status == 200
        assert response == 'foo1, foo2, foo3'
        assert endresponsecalled == 2

        when(verb='post')
        assert status == 200
        assert response == ''
        assert endresponsecalled == 3


def test_stream(app, httpreq):
    endresponsecalled = 0

    @app.when
    def endresponse(resp):
        nonlocal endresponsecalled
        endresponsecalled += 1

    @app.route()
    @y.text
    def get(req):
        yield 'foo'
        yield 'bar'
        yield 'baz'

    @app.route('/binary')
    def get(req):  # noqa: W0404
        req.response.length = 9
        yield b'foo'
        yield b'bar'
        yield b'baz'

    with httpreq():
        assert status == 200
        assert response.text == 'foobarbaz'
        assert endresponsecalled == 1

        when('/binary')
        assert status == 200
        assert response.text == 'foobarbaz'
        assert response.headers['content-length'] == '9'
        assert endresponsecalled == 2
