from yhttp import notfound
from bddrest import status, response, when


def test_routing_basic(app, Given):

    @app.route()
    def get(req):
        return 'get index'

    @app.route()
    def post(req):
        return 'post index'

    with Given():
        assert status == 200
        assert response == 'get index'

        when(verb='post')
        assert status == 200
        assert response == 'post index'

        when(verb='invalid')
        assert status == 405

        when('/invalid')
        assert status == 404


def test_routing_argument(app, Given):

    @app.route(r'/(\d+)')
    def get(req, id_):
        return id_

    with Given('/12'):
        assert status == 200
        assert response == '12'

        when('/')
        assert status == 404

        when('/foo')
        assert status == 404

        when('/1/2')
        assert status == 404

    @app.route(r'/(\d+)/?(\w+)?')
    def post(req, id_, title='Empty'):
        return f'{id_} {title}'

    with Given('/12/foo', 'post'):
        assert status == 200
        assert response == '12 foo'

        when('/12')
        assert status == 200
        assert response == '12 Empty'


def test_routing_insert(app, Given):

    @app.route(r'/(.*)')
    def get(req, id_):
        raise notfound

    @app.route(r'/foo', insert=0)
    def get(req):  # noqa: W0404
        return b'foo'

    with Given('/foo'):
        assert status == 200
        assert response == 'foo'
