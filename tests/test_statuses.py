import pytest
from bddrest import status, when, response

from yhttp.core import json, statuses


def test_status_decorator(app, httpreq):

    @app.route()
    @statuses.created()
    def post(req):
        return b''

    @app.route()
    @statuses.HTTP2xx(205)
    def put(req):
        return b''

    @app.route()
    @statuses.nocontent()
    def delete(req):
        return b''

    @app.route()
    @statuses.ok()
    def get(req):
        return b''

    with httpreq(verb='POST'):
        assert status == '201 Created'

        when(verb='PUT')
        assert status == 205

        when(verb='DELETE')
        assert status == 204
        assert response == ''

        when(verb='GET')
        assert status == 200


def test_status_raise(app, httpreq):

    with pytest.raises(ValueError):
        statuses.HTTPError(
            400,
            message='foo bar',
            contenttype='invalid content type'
        )

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
        return statuses.badrequest(message='foobarbaz')

    @app.route()
    @json
    def thud(req):
        return statuses.conflict(
            message='foo bar',
            contenttype='application/json'
        )

    with httpreq():
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
        assert response.text.startswith('400 foobarbaz\r\n')
        assert response.content_type == 'text/plain'

        when(verb='thud')
        assert status == 409
        assert response.json['status'] == 409
        assert response.json['message'] == 'foo bar'
        assert response.content_type == 'application/json'


def test_redirect(app, httpreq):

    @app.route()
    def get(req):
        raise statuses.found('http://example.com')

    with httpreq():
        assert status == 302
        assert response.headers['location'] == 'http://example.com'
        assert response.text == ''


def test_notmodified(app, httpreq):

    @app.route()
    def get(req):
        raise statuses.notmodified()

    with httpreq():
        assert status == 304
        assert response.text == ''


def test_nocontent(app, httpreq):

    @app.route()
    def remove(req):
        raise statuses.nocontent()

    with httpreq(verb='REMOVE'):
        assert status == 204
        assert response == ''


def test_unhandledexception(app, httpreq):

    class MyException(Exception):
        pass

    @app.route()
    def get(req):
        raise MyException()

    with httpreq():
        assert status == 500
        assert response.text.startswith('500 Internal Server Error')
