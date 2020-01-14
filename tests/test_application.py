from bddrest import status, response

import yhttp


def test_pipeline(app, story, when):
    endresponseiscalled = 0
    @app.when
    def endresponse():
        nonlocal endresponseiscalled
        endresponseiscalled += 1

    @app.route('/foos')
    def get(req, resp):
        assert req is not None
        assert resp is not None
        return 'foo1, foo2, foo3'

    @app.route()
    def get(req, resp):
        resp.headers.add('x-foo', 'a', 'b')
        return 'index'

    @app.route()
    def post(req, resp):
        return

    with story(app):
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


def test_stream(app, story, when):
    endresponseiscalled = 0

    @app.when
    def endresponse():
        nonlocal endresponseiscalled
        endresponseiscalled += 1

    @app.route()
    @yhttp.text
    def get(req, resp):
        yield 'foo'
        yield 'bar'
        yield 'baz'

    @app.route('/binary')
    def get(req, resp):
        resp.length = 9
        yield b'foo'
        yield b'bar'
        yield b'baz'

    with story(app):
        assert status == 200
        assert response.text == 'foobarbaz'
        assert endresponseiscalled == 1

        when('/binary')
        assert status == 200
        assert response.text == 'foobarbaz'
        assert response.headers['content-length'] == '9'
        assert endresponseiscalled == 2

