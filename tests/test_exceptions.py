import pytest
from bddrest import status, response

from yhttp import statuses


def test_httpstatus(app, story):

    @app.route()
    def get(req):
        raise statuses.badrequest()

    with story(app):
        assert status == '400 Bad Request'
        assert response.text.startswith('400 Bad Request\r\n')
        assert response.headers['content-type'] == 'text/plain; charset=utf-8'


def test_unhandledexception(app, story):

    class MyException(Exception):
        pass

    @app.route()
    def get(req):
        raise MyException()

    with pytest.raises(MyException), story(app):
        pass


def test_redirect(app, story):

    @app.route()
    def get(req):
        raise statuses.found('http://example.com')

    with story(app):
        assert status == 302
        assert response.headers['location'] == 'http://example.com'

