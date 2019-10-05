from bddrest import status, response


def test_querystringform(app, session, when):

    @app.route('/empty')
    def get():
        assert app.request.form == {}

    @app.route()
    def get():
        assert app.request.form['foo'] == 'bar'

    with session(app, query=dict(foo='bar')):
        assert status == 200

        when('/empty', query={})
        assert status == 200


def test_urlencodedform(app, session, when):

    @app.route()
    def post():
        assert app.request.contenttype == 'application/x-www-form-urlencoded'
        assert app.request.form['foo'] == 'bar'

    @app.route()
    def patch():
        assert app.request.contenttype == 'application/x-www-form-urlencoded'

    with session(app, verb='post', form=dict(foo='bar')):
        assert status == 200

        when(
            form={},
            verb='patch',
            content_type='application/x-www-form-urlencoded'
        )
        assert status == 200
        assert response == ''

def test_urlencodedform_duplicatedfield(app, session, when):

    @app.route()
    def post():
        assert app.request.form['foo'] == ['bar', 'baz']

    with session(
            app,
            verb='post',
            body='foo=bar&foo=baz',
            content_type='application/x-www-form-urlencoded'
        ):
        assert status == 200


def test_jsonform(app, session, when):
    app.settings.debug = False

    @app.route()
    def post():
        assert app.request.contenttype == 'application/json'
        assert app.request.form['foo'] == 'bar'

    with session(app, verb='post', json=dict(foo='bar')):
        assert status == 200

        # No content length
        when(body='', content_type='application/json')
        assert status == 400
        assert response.text == '400 Content-Length required'

        # Malformed
        when(body='malformed', content_type='application/json')
        assert status == 400
        assert response.text == '400 Cannot parse the request'


def test_multipartform(app, session, when):
    app.settings.debug = False

    @app.route()
    def post():
        assert app.request.contenttype.startswith('multipart/form')
        assert app.request.form['foo'] == 'bar'

    with session(app, verb='post', multipart=dict(foo='bar')):
        assert status == 200

        when(body='', content_type='multipart/form-data; boundary=')
        assert status == 400
        assert response == '400 Cannot parse the request'


