from bddrest import response, status

import yhttp.core as y


def test_jsonencoding(app, Given):

    @app.route()
    @y.json
    def get(req):
        return dict(foo='bar')

    with Given():
        assert status == 200
        assert response.json == dict(foo='bar')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'
