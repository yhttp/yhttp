from os import path

from bddrest import status, response, when

from yhttp import static


def test_staticfile(app, story, when, tmpdir):
    indexfilename = path.join(tmpdir, 'index.txt')
    with open(indexfilename, 'w') as f:
        f.write('foo')

    app.staticfile(r'/a\.txt', indexfilename)

    with story(app, '/a.txt'):
        assert status == 200
        assert response.headers['content-type'] == 'text/plain'
        assert response.headers['content-length'] == '3'
        assert response == 'foo'


def test_staticdirectory(app, story, when, tmpdir):
    indexfilename = path.join(tmpdir, 'index.txt')
    with open(indexfilename, 'w') as f:
        f.write('foo')

    app.staticdirectory(tmpdir)

    with story(app, '/index.txt'):
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

