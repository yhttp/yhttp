import io

from bddrest import status, response, when, given


def test_form_multipart(app, Given):
    app.settings.debug = False

    @app.route()
    def post(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.files is None
        assert req.form['foo'] == 'bar'

    @app.route()
    def patch(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.form['foo'] == 'bar'
        assert req.files is None

    @app.route()
    def put(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.files is None
        assert req.form['foo'] == 'bar'

    @app.route()
    def upload(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.files is not None
        assert req.files['bar'].file.read() == b'foobarbaz'

    @app.route()
    def delete(req):
        assert req.contenttype.startswith('text/plain')
        assert req.files is None

    with Given(verb='post', multipart=dict(foo='bar')):
        assert status == 200

        when(verb='patch')
        assert status == 200

        when(
            verb='upload',
            multipart=dict(bar=io.BytesIO(b'foobarbaz'))
        )
        assert status == 200

        when(verb='put', body='',
             content_type='multipart/form-data; boundary=')
        assert status == 400
        assert response == '400 Cannot parse the request'

    with Given(verb='delete', content_type='text/plain'):
        assert status == 200
