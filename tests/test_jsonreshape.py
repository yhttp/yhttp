import pytest
from bddrest import response, status, when

from yhttp.core import json_reshape


def test_jsonreshape_omit_query(app, Given):

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


def test_jsonreshape_omit(app, Given):

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

        when(query=dict(qux='baz'))
        assert status == 200
        assert response.json == dict()

        when(query=dict(qux='foo'))
        assert status == 200
        assert response.json == dict(baz='foo')

        when(query=dict(qux=''))
        assert status == 200
        assert response.json == dict(baz='foo')


def test_jsonreshape_keep_query(app, Given):

    @app.route()
    @json_reshape(keep_queryfield='qux')
    def get(req):
        return dict(
            foo='bar',
            bar='baz',
            baz='foo'
        )

    with Given():
        assert status == 200
        assert response.json == dict(foo='bar', bar='baz', baz='foo')

        when(query=dict(qux='baz'))
        assert status == 200
        assert response.json == dict(baz='foo')

        when(query=dict(qux=''))
        assert status == 200
        assert response.json == dict(foo='bar', bar='baz', baz='foo')


def test_jsonreshape_keep(app, Given):

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

        when(query=dict(qux='baz'))
        assert status == 200
        assert response.json == dict()

        when(query=dict(qux='foo'))
        assert status == 200
        assert response.json == dict(foo='bar')

        when(query=dict(qux=''))
        assert status == 200
        assert response.json == dict(foo='bar', bar='baz')


def test_jsonreshape_rename(app, Given):

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


def test_jsonreshape_simultaneous_keep_and_omit(app, Given):

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


def test_jsonreshape_list_response(app, Given):

    @app.route()
    @json_reshape(keep='foo', rename=dict(foo='qux', bar='foo'))
    def get(req):
        return [
            dict(
                foo='bar',
                bar='baz',
                baz='foo'
            ),
            dict(
                foo='bar2',
                bar='baz2',
                baz='foo2'
            ),
        ]

    with Given():
        assert status == 200
        assert response.json == [dict(foo='baz'), dict(foo='baz2')]


def test_incompatible_handlers(app, Given):

    @app.route()
    @json_reshape()
    def get(req):
        return "salam golabi"

    @app.route()
    @json_reshape()
    def post(req):
        return [1, 2, 3]

    @app.route()
    @json_reshape()
    def put(req):
        return [{"foo", "bar"}]

    with pytest.raises(AssertionError):
        with Given():
            pass

    with pytest.raises(AssertionError):
        with Given(verb='post'):
            pass

    with pytest.raises(AssertionError):
        with Given(verb='put'):
            pass
