from bddrest import status, given, when, response

from yhttp.core import statuses, guard as g, json


def test_bodyguard_strict(app, Given):
    @app.route()
    @app.bodyguard(strict=True)
    def get(req):
        pass

    @app.route()
    @app.bodyguard(strict=True, fields=(
        g.String('foo', optional=True),
        g.Integer('bar', optional=True),
    ))
    def post(req):
        pass

    with Given():
        assert status == 200

        when(form=dict(foo='bar'))
        assert status == '400 Bad Request'

    with Given(verb='post', form=dict(foo='bar')):
        assert status == 200

        when(form=given - 'foo')
        assert status == 200

        when(form=given | dict(baz='baz'))
        assert status == '400 Invalid field(s): baz'

        when(form=given | dict(bar='bar'))
        assert status == '400 bar: Integer Required'


def test_bodyguard_string(app, Given):
    @app.route()
    @app.bodyguard(fields=(
        g.String('foo', optional=True, length=(1, 3), pattern=r'^[a-z]+$'),
        g.String('baz', optional=True, length=(3, 3)),
    ))
    @json
    def post(req):
        f = req.getform(relax=True)
        return f.dict

    with Given(verb='post', form=dict(foo='abc', bar='2')):
        assert status == 200
        assert response.json == dict(foo=['abc'], bar=['2'])

        when(form=given - 'foo')
        assert status == 200

        when(form=dict(foo=''))
        assert status == '400 foo: Length must be between 1 and 3 characters'

        when(form=dict(foo='12'))
        assert status == '400 foo: Invalid Format'

        when(form=given + dict(baz='12'))
        assert status == '400 baz: Length must be 3 characters'


def test_bodyguard_integer(app, Given):
    def nozero(req, field, values):
        if values[field.name] == 0:
            raise statuses.status(400, f'{field.name}: Zero Not Allowed')

        return 0

    @app.route()
    @app.bodyguard(fields=(
        g.Integer('bar', range=(-2, 5), callback=nozero),
    ))
    @json
    def post(req):
        f = req.getform(relax=True)
        return f.dict

    with Given(verb='post', form=dict(foo='abc', bar='2')):
        assert status == 200
        assert response.json == dict(foo=['abc'], bar=[2])

        when(form=dict(bar='-2'))
        assert status == 200
        assert response.json == dict(bar=[-2])

        when(form=dict(bar='-3'))
        assert status == '400 bar: Value must be between -2 and 5'

        when(form=given - 'bar')
        assert status == '400 bar: Required'

        when(form=dict(bar='bar'))
        assert status == '400 bar: Integer Required'

        when(form=given | dict(bar=0))
        assert status == '400 bar: Zero Not Allowed'
