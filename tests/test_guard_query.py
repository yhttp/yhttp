from bddrest import status, given, when, response

from yhttp.core import statuses, guard as g, json


def test_queryguard_strict(app, Given):
    @app.route()
    @app.queryguard(strict=True)
    def get(req):
        pass

    @app.route()
    @app.queryguard(strict=True, fields=(
        g.String('foo', optional=True),
        g.Integer('bar', optional=True),
    ))
    def post(req):
        pass

    with Given():
        assert status == 200

        when(query=dict(foo='bar'))
        assert status == '400 Bad Request'

    with Given(verb='post', query=dict(foo='bar')):
        assert status == 200

        when(query=given - 'foo')
        assert status == 200

        when(query=given | dict(baz='baz'))
        assert status == '400 Invalid field(s): baz'

        when(query=given | dict(bar='bar'))
        assert status == '400 bar: Integer Required'


def test_queryguard_string(app, Given):
    @app.route()
    @app.queryguard((
        g.String('foo', optional=True, length=(1, 3), pattern=r'^[a-z]+$'),
    ))
    @json
    def post(req):
        return req.query.dict

    with Given(verb='post', query=dict(foo='abc', bar='2')):
        assert status == 200
        assert response.json == dict(foo=['abc'], bar=['2'])

        when(query=given - 'foo')
        assert status == 200

        when(query=dict(foo=''))
        assert status == '400 foo: Length must be between 1 and 3 characters'

        when(query=dict(foo='12'))
        assert status == '400 foo: Invalid Format'


def test_queryguard_integer(app, Given):
    def nozero(req, field, values):
        if values[field.name] == 0:
            raise statuses.status(400, f'{field.name}: Zero Not Allowed')

        return 0

    @app.route()
    @app.queryguard(fields=(
        g.Integer('bar', range=(-2, 5), callback=nozero),
    ))
    @json
    def post(req):
        return req.query.dict

    with Given(verb='post', query=dict(foo='abc', bar='2')):
        assert status == 200
        assert response.json == dict(foo=['abc'], bar=[2])

        when(query=dict(bar='-2'))
        assert status == 200
        assert response.json == dict(bar=[-2])

        when(query=dict(bar='-3'))
        assert status == '400 bar: Value must be between -2 and 5'

        when(query=given - 'bar')
        assert status == '400 bar: Required'

        when(query=dict(bar='bar'))
        assert status == '400 bar: Integer Required'

        when(query=given | dict(bar=0))
        assert status == '400 bar: Zero Not Allowed'
