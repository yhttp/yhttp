import pytest
from bddrest import status, response

from yhttp import statuses


def test_httpstatus(app, Given):

    @app.route()
    def get(req):
        raise statuses.badrequest()

    with Given():
        assert status == '400 Bad Request'
        assert response.text.startswith('400 Bad Request\r\n')
        assert response.headers['content-type'] == 'text/plain; charset=utf-8'


def test_unhandledexception(app, Given):

    class MyException(Exception):
        pass

    @app.route()
    def get(req):
        raise MyException()

    with pytest.raises(MyException), Given():
        pass


def test_redirect(app, Given):

    @app.route()
    def get(req):
        raise statuses.found('http://example.com')

    with Given():
        assert status == 302
        assert response.headers['location'] == 'http://example.com'
        assert response.text == ''


def test_modified(app, Given):

    @app.route()
    def get(req):
        raise statuses.notmodified()

    with Given():
        assert status == 304
        assert response.text == ''


def test_nocontent(app, Given):

    @app.route()
    def remove(req):
        raise statuses.nocontent()

    with Given(verb='REMOVE'):
        assert status == 204
        assert response == ''
