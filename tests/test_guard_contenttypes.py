from bddrest import status, when, response


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
        assert status == '400 Bad Request'
        assert response.text.startswith('400 No content-type specified\r\n')

        when(content_type='application/json')
        assert status == '400 Bad Request'
        assert response.text.startswith(
            '400 Invalid or unsupported Content-Type: application/json\r\n'
        )

        when(content_type='application/x-www-form-urlencoded')
        assert status == 200

        when(verb='PUT', content_type='application/x-www-form-urlencoded')
        assert status == 200
