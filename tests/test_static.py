from os import path

from bddrest import status, response, when


def test_staticfile(app, Given, tmpdir):
    indexfilename = path.join(tmpdir, 'index.txt')
    with open(indexfilename, 'w') as f:
        f.write('foo')

    app.staticfile(r'/a\.txt', indexfilename)

    with Given('/a.txt'):
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'


def test_staticdirectory(app, Given, mockupfs):
    temproot = mockupfs(**{
        'bar': {
            'index.txt': 'bar',
        },
        'index.txt': 'foo',
    })

    app.staticdirectory('/', temproot)

    with Given(''):
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


def test_staticdirectory_default_true(app, Given, mockupfs):
    temproot = mockupfs(**{
        'bar': {
            'index.html': 'bar',
        },
        'index.txt': 'foo',
        'index.html': 'foo bar',
    })

    app.staticdirectory('/', temproot, default=True)

    with Given(''):
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


def test_staticdirectory_default_filename(app, Given, tmpdir):
    indextxtfilename = path.join(tmpdir, 'index.txt')
    with open(indextxtfilename, 'w') as f:
        f.write('foo')

    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    app.staticdirectory('/', tmpdir, default='index.txt')

    with Given(''):
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


def test_staticdirectory_fallback_true(app, Given, tmpdir):
    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    app.staticdirectory('/', tmpdir, default=True, fallback=True)

    with Given(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/notexists.html')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'


def test_staticdirectory_fallback_file(app, Given, tmpdir):
    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    fallbackhtmlfilename = path.join(tmpdir, 'fallback.html')
    with open(fallbackhtmlfilename, 'w') as f:
        f.write('baz')

    app.staticdirectory('/', tmpdir, default=True, fallback='fallback.html')

    with Given(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/notexists.html')
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '3'
        assert response == 'baz'


def test_staticdirectory_fallback_notexistancefile(app, Given, tmpdir):
    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    app.staticdirectory('/', tmpdir, default=True, fallback='notexists.html')

    with Given(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/notexists.html')
        assert status == 404


def test_staticdirectory_autoindex(app, Given, mockupfs):
    temproot = mockupfs(**{
        'foo': {
            'foo.txt': 'foo'
        },
        'bar': {},
        'baz.txt': 'baz',
        'qux.txt': 'quz',
    })

    app.staticdirectory('/', temproot, default=True)

    with Given(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'

        when('/bar')
        assert status == 200
