import pytest
from bddrest import response, status, when

from yhttp.core import json_reshape


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

    @app.route('/no-ommit')
    @json_reshape(ommit_queryfield=None)
    def get(req):
        return dict(foo='bar')

    with Given('/no-ommit', query={'ommit-fields': 'foo'}):
        assert status == 200
        assert response.json == dict(foo='bar')


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


def test_reshape_json_rename(app, Given):

    @app.route()
    @json_reshape(rename=dict(foo='qux', bar='foo'))
    def get(req):
        return dict(
            foo='bar',
            bar='baz',
            baz='foo'
        )

    with Given():
        assert status == 200
        assert response.json == dict(qux='bar', foo='baz', baz='foo')

        when(query={'ommit-fields': 'foo'})
        assert status == 200
        assert response.json == dict(qux='bar', baz='foo')


def test_reshape_json_simultaneous_keep_and_ommit(app, Given):

    with pytest.raises(AssertionError):
        @app.route()
        @json_reshape(ommit='foo', keep='bar')
        def invalid_api(req):
            return dict()

    @app.route()
    @json_reshape(ommit_queryfield='foo', keep_queryfield='bar')
    def get(req):
        return dict()

    with Given(query=dict(foo='foo', bar='bar')):
        assert status == 400
