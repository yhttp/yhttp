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


def directory(rootpath, default=False, fallback=False):
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
    :param default: if True, the ``app.settings.staticdir.default``
                    (which default is ``index.html``) will be used as the
                    default document.
                    if ``str`` the value will be used instead of
                    ``app.settings.staticdir.default``.
    :param fallback: if ``True``, the ``app.settings.staticdir.fallback``
                    (which default is ``index.html``) will be used as the
                    fallback document if the requested resource was not found.
                    if ``str`` the value will be used instead of
                    ``app.settings.staticdir.fallback``.

    .. versionadded:: 2.13

       The *default* and *fallback* keyword arguments.

    """

    def get(request, location):
        nonlocal fallback, default

        app = request.application
        response = request.response
        target = path.join(rootpath, location)

        if default is True:
            default = app.settings.staticdir.default

        if path.isdir(target):
            if not default:
                raise statuses.forbidden()

            # Default document
            target = path.join(target, default)

        # Fallback
        if not path.exists(target):
            if fallback is None:
                raise statuses.notfound()

            if not isinstance(fallback, str):
                fallback = app.settings.staticdir.fallback

            target = path.join(rootpath, fallback)
            if not path.exists(target):
                raise statuses.notfound()

        response.length = path.getsize(target)
        response.type = guess_type(path.split(target)[1])[0]
        with open(target, 'rb') as f:
            while True:
                chunk = f.read(CHUNKSIZE)
                if not chunk:
                    break

                yield chunk

    return get
