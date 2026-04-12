from bddrest import response, status

from yhttp.core import json


def test_jsonencoding(app, httpreq):

    @app.route()
    @json
    def get(req):
        return dict(foo='bar')

    with httpreq():
        assert status == 200
        assert response.json == dict(foo='bar')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'
