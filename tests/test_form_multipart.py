from bddrest import status, response, when


def test_form_multipart(app, Given):
    app.settings.debug = False

    @app.route()
    def post(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.form['foo'] == 'bar'

    @app.route()
    def put(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.files is None
        assert req.form['foo'] == 'bar'

    with Given(verb='post', multipart=dict(foo='bar')):
        assert status == 200

        when(body='', content_type='multipart/form-data; boundary=')
        assert status == 400
        assert response == '400 Cannot parse the request'
