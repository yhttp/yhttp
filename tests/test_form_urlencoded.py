from bddrest import status, response, when


def test_form_urlencoded_malformed(app, Given):
    @app.route()
    def post(req):
        assert req.contenttype == 'application/x-www-form-urlencoded'
        assert req.form['foo'] == ['bar']

    with Given(verb='post', content_type='application/x-www-form-urlencoded',
               body='foobarbaz'):
        assert status == '400 Cannot parse the request'


def test_form_urlencoded(app, Given):

    @app.route()
    def post(req):
        assert req.contenttype == 'application/x-www-form-urlencoded'
        assert req.form['foo'] == ['bar']

    @app.route()
    def patch(req):
        assert req.contenttype == 'application/x-www-form-urlencoded'

    with Given(verb='post', form=dict(foo='bar')):
        assert status == 200

        when(
            form={},
            verb='patch',
            content_type='application/x-www-form-urlencoded'
        )
        assert status == 200
        assert response == ''


def test_form_urlencoded_duplicatefields(app, Given):

    @app.route()
    def post(req):
        assert req.form['foo'] == ['bar', 'baz']

    with Given(
            verb='post',
            body='foo=bar&foo=baz',
            content_type='application/x-www-form-urlencoded'
    ):
        assert status == 200
