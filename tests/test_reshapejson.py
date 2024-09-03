from bddrest import response, status, given, when

from yhttp.core import json_reshape


def test_reshape_json_keep_query(app, Given):

    @app.route()
    @json_reshape(keep_queryfield='qux')
    def get(req):
        return dict(
            foo='bar',
            bar='baz',
            baz='foo'
        )

    with Given(query=dict(qux='foo,baz')):
        assert status == 200
        assert response.json == dict(foo='bar', baz='foo')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'

        when(query=given - 'qux')
        assert response.json == dict(foo='bar', bar='baz', baz='foo')

        when(query=dict(qux=''))
        assert response.json == dict()


def test_reshape_json_keep(app, Given):

    @app.route()
    @json_reshape(keep='foo,bar', keep_queryfield='qux')
    def get(req):
        return dict(
            foo='bar',
            bar='baz',
            baz='foo'
        )

    with Given():
        assert status == 200
        assert response.json == dict(foo='bar', bar='baz')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'

        when(query=dict(qux='foo,baz'))
        assert status == 200
        assert response.json == dict(foo='bar')

        when(query=dict(qux=''))
        assert status == 200
        assert response.json == dict()


def test_reshape_json_ommit_query(app, Given):

    @app.route()
    @json_reshape(ommit_queryfield='qux')
    def get(req):
        return dict(
            foo='bar',
            bar='baz',
            baz='foo'
        )

    with Given(query=dict(qux='foo')):
        assert status == 200
        assert response.json == dict(bar='baz', baz='foo')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'

        when(query=dict())
        assert status == 200
        assert response.json == dict(foo='bar', bar='baz', baz='foo')

        when(query=dict(qux=''))
        assert status == 200
        assert response.json == dict(foo='bar', bar='baz', baz='foo')


def test_reshape_json_ommit(app, Given):

    @app.route()
    @json_reshape(ommit='foo,bar', ommit_queryfield='qux')
    def get(req):
        return dict(
            foo='bar',
            bar='baz',
            baz='foo'
        )

    with Given():
        assert status == 200
        assert response.json == dict(baz='foo')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == \
            'application/json; charset=utf-8'

        when(query=dict(qux='baz'))
        assert status == 200
        assert response.json == dict()

        when(query=dict(qux='foo'))
        assert status == 200
        assert response.json == dict(baz='foo')

        when(query=dict(qux=''))
        assert status == 200
        assert response.json == dict(baz='foo')
