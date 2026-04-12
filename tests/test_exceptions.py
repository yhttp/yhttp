import pytest
from bddrest import status, response, when

from yhttp.core import statuses


def test_httpstatus(app, httpreq):

    @app.route()
    def get(req):
        raise statuses.badrequest()

    @app.route('/foo')
    def get(req):
        return statuses.badrequest()

    with httpreq():
        assert status == '400 Bad Request'
        assert response.text.startswith('400 Bad Request\r\n')
        assert response.headers['content-type'] == 'text/plain; charset=utf-8'

        app.settings.debug = False
        when()
        assert status == '400 Bad Request'
        assert response.text == '400 Bad Request\r\n'
        assert response.headers['content-type'] == 'text/plain; charset=utf-8'

        when('/foo')
        assert status == 400


def test_unhandledexception(app, httpreq):

    class MyException(Exception):
        pass

    @app.route()
    def get(req):
        raise MyException()

    with pytest.raises(MyException), httpreq():
        pass


def test_redirect(app, httpreq):

    @app.route()
    def get(req):
        raise statuses.found('http://example.com')

    with httpreq():
        assert status == 302
        assert response.headers['location'] == 'http://example.com'
        assert response.text == ''


def test_modified(app, httpreq):

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
