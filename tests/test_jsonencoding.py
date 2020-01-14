from bddrest import response, status

import rehttp


def test_jsonencoding(app, story):

    @app.route()
    @rehttp.json
    def get(req, resp):
        return dict(foo='bar')

    with story(app):
        assert status == 200
        assert response.json == dict(foo='bar')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'


