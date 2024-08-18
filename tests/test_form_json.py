import ujson
from yhttp.core import statuses
from bddrest import status, response, when


def test_form_json(app, Given):

    @app.route()
    def post(req):
        assert req.contenttype == 'application/json'
        try:
            if req.json is None:
                raise statuses.lengthrequired()
        except ujson.JSONDecodeError:
            raise statuses.unprocessablecontent()

        assert req.json and req.json['foo'] == 'bar'

    @app.route()
    def get(req):
        assert req.json is None

    with Given(verb='post', json=dict(foo='bar')):
        assert status == 200

        # No content length
        when(body='', content_type='application/json')
        assert status == '411 Length Required'

        # Malformed
        when(body='malformed', content_type='application/json')
        assert status == 422

        # Empty request
        when(verb='get', json=None)
        assert status == 200


def test_form_getjson_force(app, Given):

    @app.route()
    def post(req):
        form = req.getjson()
        assert form and form['foo'] == 'bar'

    @app.route()
    def get(req):
        assert req.json is None

    with Given(verb='post', json=dict(foo='bar')):
        assert status == 200

        # No content length
        when(body='', content_type='application/json')
        assert status == '411 Length Required'

        # Malformed
        when(body='malformed', content_type='application/json')
        assert status == 422

        # Empty request
        when(verb='get', json=None)
        assert status == 200


def test_form_getjson_relax(app, Given):

    @app.route()
    def post(req):
        form = req.getjson(relax=True)
        if form is None:
            return 'None'

        return form['foo']

    @app.route()
    def get(req):
        assert req.json is None

    with Given(verb='post', json=dict(foo='bar')):
        assert status == 200
        assert response.text == 'bar'

        # No content length
        when(body='', content_type='application/json')
        assert status == 200
        assert response.text == 'None'

        # Malformed
        when(body='malformed', content_type='application/json')
        assert status == 200
        assert response.text == 'None'

        # Empty request
        when(verb='get', json=None)
        assert status == 200
