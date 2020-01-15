from mimetypes import guess_type
from os import path

from . import statuses


CHUNKSIZE = 1024 * 10


def file(filename):
    length = path.getsize(filename)
    type_ = guess_type(path.split(filename)[1])[0]
    def get(request):
        response = request.response
        response.length = length
        response.type = type_
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(CHUNKSIZE)
                if not chunk:
                    break

                yield chunk

    return get


def directory(rootpath):
    def get(request, location):
        response = request.response
        filename = path.join(rootpath, location)

        if not path.exists(filename):
            raise statuses.notfound()

        response.length = path.getsize(filename)
        response.type = guess_type(path.split(filename)[1])[0]
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(CHUNKSIZE)
                if not chunk:
                    break

                yield chunk

    return get

