import io

from bddrest import status, when

from yhttp.core.multidict import MultiDict


def test_form_multipart(app, Given):
    app.settings.debug = False

    @app.route()
    def post(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.files is not None
        assert isinstance(req.files, MultiDict)
        assert req.form['foo'] == 'bar'

    @app.route()
    def patch(req):
        assert req.contenttype.startswith('multipart/form')
        assert isinstance(req.files, MultiDict)
        assert req.form['foo'] == 'bar'

    @app.route()
    def put(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.getform()['foo'] == 'bar'

    @app.route()
    def upload(req):
        assert req.getfiles()['bar'].file.read() == b'foobarbaz'

    @app.route()
    def get(req):
        assert req.getform(relax=True) is None
        assert req.getfiles(relax=True) is None

    @app.route()
    def head(req):
        assert req.getfiles()

    @app.route()
    def delete(req):
        assert req.contenttype.startswith('text/plain')
        assert req.getfiles(relax=True) is None

    with Given(verb='post', multipart=dict(foo='bar')):
        assert status == 200

        when(verb='patch')
        assert status == 200

        when(verb='head')
        assert status == 422

        when(verb='get')
        assert status == 200

        when(
            verb='upload',
            multipart=dict(bar=io.BytesIO(b'foobarbaz'))
        )
        assert status == 200

        when(
            verb='upload',
            multipart=dict()
        )
        assert status == 411

        when(verb='put', body='',
             content_type='multipart/form-data; boundary=')
        assert status == 411

    with Given(verb='delete', content_type='text/plain'):
        assert status == 200
