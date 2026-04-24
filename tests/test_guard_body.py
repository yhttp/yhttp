import io

from bddrest import status, given, when, response

from yhttp.core import statuses, guard as g, json
from yhttp.core.multidict import MultiDict


def test_bodyguard_strict(app, httpreq):
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

    with httpreq():
        assert status == 200

        when(form=dict(foo='bar'))
        assert status == '400 Bad Request'

    with httpreq(verb='post', form=dict(foo='bar')):
        assert status == 200

        when(form=given - 'foo')
        assert status == 200

        when(form=given | dict(baz='baz'))
        assert status == '400 Invalid field(s): baz'

        when(form=given | dict(bar='bar'))
        assert status == '400 bar: Integer Required'


def test_bodyguard_string(app, httpreq):
    @app.route()
    @app.bodyguard(fields=(
        g.String('foo', optional=True, length=(1, 3), pattern=r'^[a-z]+$'),
        g.String('baz', optional=True, length=(3, 3)),
    ))
    @json
    def post(req):
        f = req.getform(relax=True)
        return f.dict

    with httpreq(verb='post', form=dict(foo='abc', bar='2')):
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


def test_bodyguard_integer(app, httpreq):
    def nozero(req, field, values):
        if values[field.name] == 0:
            raise statuses.HTTPStatus(400, f'{field.name}: Zero Not Allowed')

        return 0

    @app.route()
    @app.bodyguard(fields=(
        g.Integer('bar', range=(-2, 5), callback=nozero),
    ))
    @json
    def post(req):
        f = req.getform(relax=True)
        return f.dict

    with httpreq(verb='post', form=dict(foo='abc', bar='2')):
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


def test_bodyguard_multipart(app, httpreq):
    app.settings.debug = False
    bazfile = g.File('baz')

    @app.route()
    @app.bodyguard(fields=(
        g.String('foo'),
        g.Integer('bar'),
        bazfile,
    ))
    def post(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.files is not None
        assert isinstance(req.files, MultiDict)
        assert req.form['foo'] == 'FOO'
        assert req.form['bar'] == 73
        assert req.files['baz']

    @app.route()
    @app.bodyguard(fields=(
        g.String('foo'),
        g.Integer('bar'),
        bazfile(optional=True, extensions=['.jpg']),
    ))
    def put(req):
        assert req.contenttype.startswith('multipart/form')
        assert req.files is not None
        assert isinstance(req.files, MultiDict)
        assert req.form['foo'] == 'FOO'
        assert req.form['bar'] == 73
        if 'baz' in req.files:
            assert req.files['baz']

    file = io.BytesIO(b'foobarbaz')
    form = dict(
        foo='FOO',
        bar='73',
        baz=file,
    )
    with httpreq(verb='post', multipart=form):
        assert status == 200

        when(multipart=given - 'baz')
        assert status == 400

        when(verb='PUT', multipart=given - 'baz')
        assert status == 200

        when(verb='PUT')
        assert status == 400

        file.name = 'baz.jpg'
        when(verb='PUT')
        assert status == 200
