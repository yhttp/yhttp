from bddrest import status, response, when


def test_form_json(app, Given):
    app.settings.debug = False

    @app.route()
    def post(req):
        assert req.contenttype == 'application/json'
        assert req.json and req.json['foo'] == 'bar'

    @app.route()
    def get(req):
        assert req.json is None

    with Given(verb='post', json=dict(foo='bar')):
        assert status == 200

        # No content length
        when(body='', content_type='application/json')
        assert status == 400
        assert response.text == '400 Content-Length required'

        # Malformed
        when(body='malformed', content_type='application/json')
        assert status == 400
        assert response.text == '400 `ujson`: Cannot parse the request'

        # Empty request
        when(verb='get', json=None)
        assert status == 200
