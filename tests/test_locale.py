from bddrest import status, when, response

from yhttp.core import json


def test_locales(app, httpreq):
    @app.route()
    @json
    def get(req):
        return [req.locales, req.language]

    with httpreq(headers={'Accept-Languages': 'en-US,*;q=0.5,fa;q=0.7'}):
        assert status == 200
        assert response.json == [['en-US', 'fa', '*'], 'en']

        when(headers={})
        assert status == 200
        assert response.json == [['*'], None]

        when(headers={'Accept-Languages': ';;'})
        assert status == 400

        when(headers={'Accept-Languages': 'en,fa;q'})
        assert status == 400

        when(headers={'Accept-Languages': 'en,fa;q=x'})
        assert status == 400
