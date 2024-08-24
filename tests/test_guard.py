from bddrest import status, given, when

from yhttp.core import guard


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
