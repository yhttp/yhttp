from os import path
from types import SimpleNamespace

from bddrest import status, response, when
import pytest

from yhttp.core.headerset import HeaderSet
from yhttp.core.static import file as staticfile


def test_staticfile(app, httpreq, tmpdir):
    indexfilename = path.join(tmpdir, 'index.txt')
    with open(indexfilename, 'w') as f:
        f.write('foo')

    app.staticfile(r'/a\.txt', indexfilename)

    with httpreq('/a.txt'):
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'


def test_staticfile_byte_ranges(app, httpreq, tmpdir):
    filename = path.join(tmpdir, 'range.txt')
    with open(filename, 'wb') as f:
        f.write(b'0123456789')

    app.staticfile(r'/range\.txt', filename)

    with httpreq('/range.txt', headers={'Range': 'bytes=2-5'}):
        assert status == 206
        assert response.headers['accept-ranges'] == 'bytes'
        assert response.headers['content-range'] == 'bytes 2-5/10'
        assert response.headers['content-length'] == '4'
        assert response == '2345'

    with httpreq('/range.txt', headers={'Range': 'bytes=-3'}):
        assert status == 206
        assert response.headers['content-range'] == 'bytes 7-9/10'
        assert response == '789'

    with httpreq('/range.txt', headers={'Range': 'bytes=20-'}):
        assert status == 416
        assert response.headers['content-range'] == 'bytes */10'

    with httpreq('/range.txt', headers={'Range': 'bytes=-0'}):
        assert status == 416
        assert response.headers['content-range'] == 'bytes */10'

    with httpreq('/range.txt', headers={'Range': 'invalid'}):
        assert status == 200
        assert response.headers['content-length'] == '10'
        assert response == '0123456789'

    with httpreq(
        '/range.txt', headers={'Range': 'bytes=0-1,4-5'}
    ):
        assert status == 200
        assert response == '0123456789'


@pytest.mark.parametrize('range_header', [
    'bytes=10',
    'bytes=-',
    'bytes=3-1',
    'bytes=abc-def',
    'bytes=--1',
])
def test_malformed_or_unsupported_ranges_send_full_file(
    app, httpreq, tmpdir, range_header,
):
    filename = path.join(tmpdir, 'range.txt')
    with open(filename, 'wb') as f:
        f.write(b'0123456789')
    app.staticfile(r'/range\.txt', filename)

    with httpreq('/range.txt', headers={'Range': range_header}):
        assert status == 200
        assert response == '0123456789'


def test_empty_static_file(app, httpreq, tmpdir):
    filename = path.join(tmpdir, 'empty.txt')
    open(filename, 'wb').close()
    app.staticfile(r'/empty\.txt', filename)

    with httpreq('/empty.txt'):
        assert status == 200
        assert response.headers['content-length'] == '0'
        assert response == ''


def test_staticfile_short_read_after_size_lookup(tmpdir):
    filename = path.join(tmpdir, 'short.txt')
    with open(filename, 'wb') as f:
        f.write(b'content')

    handler = staticfile(filename)
    request = SimpleNamespace(
        verb='get', environ={},
        response=SimpleNamespace(headers=HeaderSet()),
    )
    open(filename, 'wb').close()

    assert list(handler(request)) == []


def test_staticdirectory_byte_ranges(app, httpreq, tmpdir):
    filename = path.join(tmpdir, 'range.txt')
    with open(filename, 'wb') as f:
        f.write(b'0123456789')
    app.staticdirectory('/static', tmpdir)

    with httpreq('/static/range.txt', headers={'Range': 'bytes=3-'}):
        assert status == 206
        assert response.headers['content-range'] == 'bytes 3-9/10'
        assert response == '3456789'


def test_range_request_with_if_range_sends_full_file(app, httpreq, tmpdir):
    filename = path.join(tmpdir, 'range.txt')
    with open(filename, 'wb') as f:
        f.write(b'0123456789')
    app.staticfile(r'/range\.txt', filename)

    with httpreq('/range.txt', headers={
        'Range': 'bytes=2-5',
        'If-Range': '"unknown-validator"',
    }):
        assert status == 200
        assert response == '0123456789'


def test_staticdirectory(app, httpreq, mktmptree):
    temproot = mktmptree({
        'bar': {
            'index.txt': 'bar',
        },
        'index.txt': 'foo',
    })

    app.staticdirectory('/static', temproot)

    with httpreq('/static'):
        assert status == 403

        when('/static/')
        assert status == 403

        when('/static/index.txt')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'

        when('/static/bar')
        assert status == 403

        when('/static/bar/index.txt')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'bar'

        when('/static/invalidfile')
        assert status == 404

        when('/invalid/file')
        assert status == 404

        when('/invalid/file.html')
        assert status == 404


def test_staticdirectory_root(app, httpreq, mktmptree):
    temproot = mktmptree({
        'bar': {
            'index.txt': 'bar',
        },
        'index.txt': 'foo',
    })

    app.staticdirectory('/', temproot)

    with httpreq(''):
        assert status == 403

        when('/')
        assert status == 403

        when('/index.txt')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'

        when('/bar')
        assert status == 403

        when('/bar/index.txt')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'bar'

        when('/invalidfile')
        assert status == 404

        when('/invalid/file')
        assert status == 404

        when('/invalid/file.html')
        assert status == 404


def test_staticdirectory_default_true(app, httpreq, mktmptree):
    temproot = mktmptree({
        'bar': {
            'index.html': 'bar',
        },
        'index.txt': 'foo',
        'index.html': 'foo bar',
    })

    app.staticdirectory('/', temproot, default=True)

    with httpreq(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/index.txt')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'

        when('/bar')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '3'
        assert response == 'bar'

        when('/bar/')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '3'
        assert response == 'bar'

        when('/invalidfile')
        assert status == 404

        when('/invalid/file')
        assert status == 404

        when('/invalid/file.html')
        assert status == 404


def test_staticdirectory_default_filename(app, httpreq, tmpdir):
    indextxtfilename = path.join(tmpdir, 'index.txt')
    with open(indextxtfilename, 'w') as f:
        f.write('foo')

    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    app.staticdirectory('/', tmpdir, default='index.txt')

    with httpreq(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'

        when('/')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'

        when('/index.txt')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'

        when('/index.html')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/invalidfile')
        assert status == 404

        when('/invalid/file')
        assert status == 404

        when('/invalid/file.html')
        assert status == 404


def test_staticdirectory_fallback_true(app, httpreq, tmpdir):
    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    app.staticdirectory('/', tmpdir, default=True, fallback=True)

    with httpreq(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/notexists.html')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'


def test_staticdirectory_fallback_file(app, httpreq, tmpdir):
    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    fallbackhtmlfilename = path.join(tmpdir, 'fallback.html')
    with open(fallbackhtmlfilename, 'w') as f:
        f.write('baz')

    app.staticdirectory('/', tmpdir, default=True, fallback='fallback.html')

    with httpreq(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/notexists.html')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '3'
        assert response == 'baz'


def test_staticdirectory_fallback_notexistancefile(app, httpreq, tmpdir):
    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    app.staticdirectory('/', tmpdir, default=True, fallback='notexists.html')

    with httpreq(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/notexists.html')
        assert status == 404


def test_staticdirectory_autoindex(app, httpreq, mktmptree):
    temproot = mktmptree({
        'foo': {
            'foo.txt': 'foo'
        },
        'bar': {},
        'baz.txt': 'baz',
        'qux.txt': 'quz',
    })

    app.staticdirectory('/', temproot, default=True)

    with httpreq(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'

        when('/bar')
        assert status == 200
