from yhttp.core import text, statuses

from bddrest import response, when, given, status


def test_from(app, httpreq):
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

    with httpreq(verb='POST', form={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'

        when(form=given - 'foo')
        assert status == 400

    with httpreq(verb='POST', form={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'

    with httpreq(verb='POST', multipart={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'


def test_getform_force(app, httpreq):
    @app.route()
    @text
    def post(req):
        return req.getform()['foo']

    with httpreq(verb='POST', form={'foo': 'bar'}):
        assert status == 200
        assert response.text == 'bar'

        when(form=given - 'foo')
        assert status == 411

        when(body='foo!bar?baz')
        assert status == 422
