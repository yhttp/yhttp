from urllib.parse import quote

from bddrest import status, response, when, Given

import yhttp.core as y


def test_rewrite_nodefault():
    log = []
    foo = y.Application()
    bar = y.Application()
    app = y.Rewrite()
    app.route(r'/foo/?', r'/', foo)
    app.route(r'/bar/?', r'/', bar)

    @app.when
    def endresponse(app):
        log.append('app endresponse')

    @foo.route()
    @y.statuscode('201 Created')
    def get(req):
        return 'foo'

    @bar.route()
    def get(req):
        return 'bar'

    with Given(app):
        assert status == 404

        when('/qux')
        assert status == 404

        when('/foo')
        assert status == 201
        assert response.text == 'foo'

        when('/bar')
        assert status == 200
        assert response.text == 'bar'

    assert log == [
        'app endresponse',
        'app endresponse',
    ]


def test_rewrite_default():
    root = y.Application()
    foo = y.Application()
    app = y.Rewrite(default=root)
    app.route(r'/foo/?(.*)', r'/\1', foo)

    @root.route()
    def get(req):
        return 'root'

    @foo.route()
    @y.statuscode('201 Created')
    def get(req):
        resp = 'foo'
        if req.query:
            qs = ', '.join(f'{k}={v}' for k, v in req.query.items())
            resp += f' qs: {qs}'

        return resp

    with Given(app):
        assert status == 200
        assert response.text == 'root'

        when('/qux')
        assert status == 404

        when('/foo?bar=baz')
        assert status == 201
        assert response.text == 'foo qs: bar=baz'

        when('/foo')
        assert status == 201
        assert response.text == 'foo'

        when('/foo?bar=baz')
        assert status == 201
        assert response.text == 'foo qs: bar=baz'


def test_rewrite_hooks():
    log = []
    root = y.Application()
    foo = y.Application()
    app = y.Rewrite(default=root)
    app.route(r'/foo/?(.*)', r'/\1', foo)

    @app.when
    def ready(app):
        log.append('app ready')

    @root.when
    def ready(app):
        log.append('root ready')

    @foo.when
    def ready(app):
        log.append('foo ready')

    @root.when
    def endresponse(app):
        log.append('root endresponse')

    @foo.when
    def endresponse(app):
        log.append('foo endresponse')

    @app.when
    def shutdown(app):
        log.append('app shutdown')

    @root.when
    def shutdown(app):
        log.append('root shutdown')

    @foo.when
    def shutdown(app):
        log.append('foo shutdown')

    @root.route()
    def get(req):
        return 'root'

    @foo.route()
    @y.statuscode('201 Created')
    def get(req):
        return 'foo'

    app.ready()

    with Given(app):
        assert status == 200
        assert response.text == 'root'

        when('/foo')
        assert status == 201
        assert response.text == 'foo'

        when('/bar')
        assert status == 404

    app.shutdown()
    assert log == [
        'foo ready',
        'root ready',
        'app ready',

        'root endresponse',
        'foo endresponse',
        'root endresponse',

        'foo shutdown',
        'root shutdown',
        'app shutdown',
    ]


def test_rewrite_encodedurl():
    root = y.Application()
    foo = y.Application()
    app = y.Rewrite(default=root)
    app.route(r'/foo/?(.*)', r'/\1', foo)

    @root.route()
    def get(req):
        return 'root'

    @foo.route(r'/(.+)')
    @y.statuscode('201 Created')
    def get(req, arg):
        resp = f'foo: {arg}'
        if req.query:
            qs = ', '.join(f'{k}={v}' for k, v in req.query.items())
            resp += f' qs: {qs}'

        return resp

    with Given(app):
        assert status == 200
        assert response.text == 'root'

        when('/foo/bar')
        assert status == 201
        assert response.text == 'foo: bar'

        when(quote('/foo/الف'))
        assert status == 201
        assert response.text == 'foo: الف'

        when(quote('/foo/الف?a=ابجد'))
        assert status == 201
        assert response.text == 'foo: الف?a=ابجد'
