import pytest
from bddrest import response, status, when

from yhttp.core import json_reshape


def test_reshape_json_omit_query(app, Given):

    @app.route()
    @json_reshape(omit_queryfield='qux')
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

    @app.route('/no-omit')
    @json_reshape(omit_queryfield=None)
    def get(req):
        return dict(foo='bar')

    with Given('/no-omit', query={'omit-fields': 'foo'}):
        assert status == 200
        assert response.json == dict(foo='bar')


def test_reshape_json_omit(app, Given):

    @app.route()
    @json_reshape(omit='foo,bar', omit_queryfield='qux')
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

        when(query={'omit-fields': 'foo'})
        assert status == 200
        assert response.json == dict(qux='bar', baz='foo')


def test_reshape_json_simultaneous_keep_and_omit(app, Given):

    with pytest.raises(AssertionError):
        @app.route()
        @json_reshape(omit='foo', keep='bar')
        def invalid_api(req):
            return dict()

    @app.route()
    @json_reshape(omit_queryfield='foo', keep_queryfield='bar')
    def get(req):
        return dict()

    with Given(query=dict(foo='foo', bar='bar')):
        assert status == 400
