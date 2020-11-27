from bddrest import response, status

import yhttp


def test_jsonencoding(app, Given):

    @app.route()
    @yhttp.json
    def get(req):
        return dict(foo='bar')

    with Given():
        assert status == 200
        assert response.json == dict(foo='bar')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'
