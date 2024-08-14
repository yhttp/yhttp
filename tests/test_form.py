from yhttp import text, statuses

from bddrest import response, when, given, status


def test_from(app, Given):
    @app.route()
    @text
    def post(req):
        try:
            from pudb import set_trace; set_trace()
            return req.form['foo']
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
