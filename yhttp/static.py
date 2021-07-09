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


def directory(rootpath, default=None):
    """Create a static directory handler.

    So the files inside the directory are accessible by their names:

    .. code-block::

        app.route(r'/public/(.*)', directory('public'))

    Or simply:

    .. code-block::

        app.staticdirectory('/foo/', 'physical/path/to/foo')

    You you can do:

    .. code-block:: bash

       curl localhost:8080/public/foo.html

    .. seealso::

       :ref:`cookbook-static`

    :param directory: Static files are here.
    :param default: if None, the ``app.settings.staticdir.default``
                    (which default is ``index.html``) will be used as the
                    default document.

    .. versionadded:: 2.13

       ``default``
    """

    def get(request, location):
        response = request.response

        if not location:
            location = default or \
                request.application.settings.staticdir.default

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
