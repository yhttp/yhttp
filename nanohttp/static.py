from os import path
from mimetypes import guess_type

from . import statuses


CHUNKSIZE = 1024 * 10


def file(app, filename):
    length = path.getsize(filename)
    type_ = guess_type(path.split(filename)[1])[0]
    def get():
        app.response.length = length
        app.response.type = type_
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(CHUNKSIZE)
                if not chunk:
                    break

                yield chunk

    return get


def directory(app, rootpath):
    def get(location):
        filename = path.join(rootpath, location)

        if not path.exists(filename):
            raise statuses.notfound()

        app.response.length = path.getsize(filename)
        app.response.type = guess_type(path.split(filename)[1])[0]
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(CHUNKSIZE)
                if not chunk:
                    break

                yield chunk


    return get
