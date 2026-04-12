from os import path

from bddrest import status, response, when


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
