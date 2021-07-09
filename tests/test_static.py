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


def test_staticdirectory(app, Given, tmpdir):
    indextxtfilename = path.join(tmpdir, 'index.txt')
    with open(indextxtfilename, 'w') as f:
        f.write('foo')

    indexhtmlfilename = path.join(tmpdir, 'index.html')
    with open(indexhtmlfilename, 'w') as f:
        f.write('foo bar')

    app.staticdirectory('/', tmpdir)

    with Given(''):
        assert status == 200
        assert response.headers['content-type'] == 'text/html'
        assert response.headers['content-length'] == '7'
        assert response == 'foo bar'

        when('/index.txt')
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'

        when('/invalidfile')
        assert status == 404

        when('/invalid/file')
        assert status == 404

        when('/invalid/file.html')
        assert status == 404
