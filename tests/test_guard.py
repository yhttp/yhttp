import pytest
from bddrest import status, given, when, response

from yhttp.core import guard, json


def test_guard_override(app, Given):
    bar = guard.String('bar', optional=True)
    qux = guard.Integer('qux', range=(0, 3), optional=True)
    quux = guard.Boolean('quux', default=False)

    @app.route()
    @app.bodyguard((
        bar(length=(3, 5)),
        bar(name='baz', optional=False),
        qux(range=(0, 5)),
        quux(),
    ))
    @json
    def post(req):
        return req.form.dict

    with Given(verb='post', form=dict(bar='bar', baz='baz', quux='False')):
        assert status == 200
        assert response.json == dict(bar=['bar'], baz=['baz'], quux=[False])

        when(form=given - 'bar')
        assert status == 200
        assert response.json == dict(baz=['baz'], quux=[False])

        when(form=given | dict(bar='12'))
        assert status == '400 bar: Length must be between 3 and 5 characters'

        when(form=given - 'baz')
        assert status == '400 baz: Required'

        when(form=given | dict(qux='12'))
        assert status == '400 qux: Value must be between 0 and 5'

        when(form=given | dict(qux='5'))
        assert status == 200
        assert response.json == dict(bar=['bar'], baz=['baz'], qux=[5],
                                     quux=[False])

        when(form=given - 'quux')
        assert status == 200
        assert response.json == dict(bar=['bar'], baz=['baz'], quux=[False])

        when(form=given | dict(quux='yes'))
        assert status == 200
        assert response.json == dict(bar=['bar'], baz=['baz'], quux=[True])

        when(form=given | dict(quux='true'))
        assert status == 200
        assert response.json == dict(bar=['bar'], baz=['baz'], quux=[True])

        when(form=given | dict(quux='ok'))
        assert status == 200
        assert response.json == dict(bar=['bar'], baz=['baz'], quux=[True])

        when(form=given | dict(quux=''))
        assert status == '400 quux: Boolean Required'


def test_guard(app, Given):
    @app.route()
    @app.queryguard((
        guard.String('foo'),
    ), strict=True)
    @app.bodyguard((
        guard.String('bar'),
        guard.String('baz', optional=True)
    ))
    def post(req):
        pass

    with Given(verb='post', query=dict(foo='foo'),
               form=dict(bar='bar', baz='baz')):
        assert status == 200

        when(form=given - 'bar')
        assert status == '400 bar: Required'

        when(form=given - 'baz', query=given + dict(baz='baz'))
        assert status == '400 Invalid field(s): baz'

        when(form=given - 'baz')
        assert status == 200


def test_guard_default(app, Given):
    with pytest.raises(AssertionError):
        guard.String('foo', default='def')

    def foodef(req, self, values):
        return 'foodef'

    @app.route()
    @app.queryguard((
        guard.String('foo', optional=True, default=foodef),
    ), strict=True)
    @app.bodyguard((
        guard.String('bar', optional=True, default='bardef'),
    ))
    @json
    def post(req):
        return dict(
            foo=req.query['foo'],
            bar=req.form['bar'],
        )

    with Given(verb='post'):
        assert status == 200
        assert response.json == dict(foo='foodef', bar='bardef')

        when(query=dict(foo='abc'))
        assert status == 200
        assert response.json == dict(foo='abc', bar='bardef')

        when(form=dict(bar='cba'))
        assert status == 200
        assert response.json == dict(foo='foodef', bar='cba')

        when(query=dict(foo='abc'), form=dict(bar='cba'))
        assert status == 200
        assert response.json == dict(foo='abc', bar='cba')
