from bddrest import status, response, when

import yhttp.core as y


def test_pipeline(app, Given):
    endresponseiscalled = 0

    @app.when
    def endresponse(resp):
        nonlocal endresponseiscalled
        endresponseiscalled += 1

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

    with Given():
        assert status == 200
        assert response == 'index'
        assert 'content-type' not in response.headers
        assert 'x-foo' in response.headers
        assert endresponseiscalled == 1

        when('/foos')
        assert status == 200
        assert response == 'foo1, foo2, foo3'
        assert endresponseiscalled == 2

        when(verb='post')
        assert status == 200
        assert response == ''
        assert endresponseiscalled == 3


def test_stream(app, Given):
    endresponseiscalled = 0

    @app.when
    def endresponse(resp):
        nonlocal endresponseiscalled
        endresponseiscalled += 1

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

    with Given():
        assert status == 200
        assert response.text == 'foobarbaz'
        assert endresponseiscalled == 1

        when('/binary')
        assert status == 200
        assert response.text == 'foobarbaz'
        assert response.headers['content-length'] == '9'
        assert endresponseiscalled == 2
