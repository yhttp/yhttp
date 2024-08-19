from bddrest import response, status, when

from yhttp.core import json, statuses


def test_httpstatus(app, Given):

    @app.route()
    @json
    def get(req):
        return dict(foo='bar')

    @app.route()
    @json
    def bar(req):
        req.response.headers.add('x-bar', 'bar')
        raise statuses.nocontent()

    @app.route()
    @json
    def baz(req):
        req.response.headers.add('x-baz', 'baz')
        raise statuses.badrequest()

    @app.route()
    @json
    def qux(req):
        req.response.headers.add('x-qux', 'qux')
        return statuses.badrequest()

    with Given():
        assert status == 200
        assert response.json == dict(foo='bar')

        when(verb='bar')
        assert status == 204
        assert response.headers['x-bar'] == 'bar'

        when(verb='baz')
        assert status == 400
        assert 'x-baz' not in response.headers

        when(verb='qux')
        assert status == 400
        assert 'x-qux' not in response.headers
