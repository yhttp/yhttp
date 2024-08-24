import pytest
from bddrest import status, given, when, response

from yhttp.core import guard, json


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
