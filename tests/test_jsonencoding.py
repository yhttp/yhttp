from bddrest import response, status

from yhttp.core import json


def test_jsonencoding(app, Given):

    @app.route()
    @json
    def get(req):
        return dict(foo='bar')

    with Given():
        assert status == 200
        assert response.json == dict(foo='bar')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'
