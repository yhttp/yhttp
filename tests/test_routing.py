from bddrest import status, response


def test_routing_basic(app, session, when):

    @app.route()
    def get():
        return 'get index'

    @app.route()
    def post():
        return 'post index'

    with session(app):
        assert status == 200
        assert response == 'get index'

        when(verb='post')
        assert status == 200
        assert response == 'post index'

        when(verb='invalid')
        assert status == 405

        when('/invalid')
        assert status == 404


def test_routing_argument(app, session, when):

    @app.route(r'/(\d+)')
    def get(id):
        return id

    with session(app, '/12'):
        assert status == 200
        assert response == '12'

        when('/')
        assert status == 404

        when('/foo')
        assert status == 404

        when('/1/2')
        assert status == 404


    @app.route(r'/(\d+)/(\w*)')
    def post(id, title):
        return f'{id} {title}'

    with session(app, '/12/foo', 'post'):
        assert status == 200
        assert response == '12 foo'

        when('/12')
        assert status == 404


