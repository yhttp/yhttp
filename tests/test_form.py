from yhttp.core import text, statuses

from bddrest import response, when, given, status


def test_from(app, Given):
    @app.route()
    @text
    def post(req):
        form = req.getform(relax=True)
        if form is None:
            raise statuses.badrequest()

        try:
            return form['foo']
        except KeyError:
            raise statuses.badrequest()

    with Given(verb='POST', form={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'

        when(form=given - 'foo')
        assert status == 400

    with Given(verb='POST', form={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'

    with Given(verb='POST', multipart={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'


def test_getform_force(app, Given):
    @app.route()
    @text
    def post(req):
        return req.getform()['foo']

    with Given(verb='POST', form={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'

        when(form=given - 'foo')
        assert status == 411

        when(body='foo!bar?baz')
        assert status == 422
