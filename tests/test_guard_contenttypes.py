from bddrest import status, when


def test_bodyguard_contenttypes(app, httpreq):
    @app.route()
    @app.bodyguard(contenttypes='application/x-www-form-urlencoded')
    def post(req):
        pass

    @app.route()
    @app.bodyguard(contenttypes=[
        'application/x-www-form-urlencoded',
        'multipart/form'
    ])
    def put(req):
        pass

    with httpreq(verb='POST'):
        assert status == '400 No content-type specified'

        when(content_type='application/json')
        assert status == '400 Invalid content-type: application/json'

        when(content_type='application/x-www-form-urlencoded')
        assert status == 200

        when(verb='PUT', content_type='application/x-www-form-urlencoded')
        assert status == 200
