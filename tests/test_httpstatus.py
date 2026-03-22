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

    @app.route()
    @json
    def quux(req):
        return statuses.badrequest(body='foobarbaz')

    @app.route()
    @json
    def thud(req):
        return statuses.conflict(body=dict(foo='bar'))

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

        when(verb='quux')
        assert status == 400
        assert response == 'foobarbaz'
        assert response.content_type == 'text/plain'

        when(verb='thud')
        assert status == 409
        assert response.json == dict(foo='bar')
        assert response.content_type == 'application/json'
