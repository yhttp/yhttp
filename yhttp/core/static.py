import os
from mimetypes import guess_type
from os import path

from . import statuses


CHUNKSIZE = 1024 * 10


def _byte_range(request, length):
    """Return the selected byte interval, or None when Range is ignored."""
    if request.verb != 'get' or 'HTTP_IF_RANGE' in request.environ:
        return None

    value = request.environ.get('HTTP_RANGE')
    if not value or '=' not in value:
        return None

    unit, spec = value.split('=', 1)
    if unit.strip().lower() != 'bytes' or ',' in spec:
        # Multiple ranges are optional; ignore them and send the full entity.
        return None

    spec = spec.strip()
    if '-' not in spec:
        return None
    first, last = (part.strip() for part in spec.split('-', 1))
    if not first and not last:
        return None

    try:
        if not first:
            suffix_length = int(last)
            if suffix_length < 0:
                return None
            if suffix_length == 0 or length == 0:
                return False
            return max(0, length - suffix_length), length - 1

        start = int(first)
        if last:
            end = int(last)
            if end < start:
                return None
        else:
            end = length - 1
    except ValueError:
        return None

    if start >= length:
        return False
    return start, min(end, length - 1)


def _stream_file(request, filename, length, contenttype):
    response = request.response
    response.contenttype = contenttype
    response.headers['accept-ranges'] = 'bytes'

    byte_range = _byte_range(request, length)
    if byte_range is False:
        response.status = '416 Range Not Satisfiable'
        response.headers['content-range'] = f'bytes */{length}'
        response.length = 0
        yield b''
        return

    if byte_range is None:
        response.length = length
        start, end = 0, length - 1
    else:
        start, end = byte_range
        response.status = '206 Partial Content'
        response.headers['content-range'] = f'bytes {start}-{end}/{length}'
        response.length = end - start + 1

    if not response.length:
        yield b''
        return

    with open(filename, 'rb') as f:
        f.seek(start)
        remaining = response.length
        while remaining:
            chunk = f.read(min(CHUNKSIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


def file(filename):
    length = path.getsize(filename)
    type_ = guess_type(path.split(filename)[1])[0]

    def get(request):
        yield from _stream_file(request, filename, length, type_)

    return get


def index(directory):
    rel = path.relpath(directory)
    rel = '' if rel == '.' else rel

    lines = [
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="UTF-8"/>'
        f'<title>Index of /{rel}</title>'
        '</head><body>'
    ]
    dirs = []
    files = []
    for f in os.listdir(directory):
        if path.isdir(path.join(directory, f)):
            dirs.append(f)
        else:
            files.append(f)

    for d in sorted(dirs):
        lines.append(f'<a href="{d}/">{d}/</a></br>')

    for f in sorted(files):
        lines.append(f'<a href="{f}">{f}</a></br>')

    lines += [
        '</body>'
    ]

    return '\n'.join(lines)


def directory(rootpath, default=False, autoindex=True, fallback=False):
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
    :param autoindex: if True, automatically serve an index of available files
                      within current path.
    :param fallback: if ``True``, the ``app.settings.staticdir.fallback``
                    (which default is ``index.html``) will be used as the
                    fallback document if the requested resource was not found.
                    if ``str`` the value will be used instead of
                    ``app.settings.staticdir.fallback``.

    .. versionadded:: 2.13

       The *default* and *fallback* keyword arguments.

    .. versionadded:: 3.8

       The *autoindex* keyword argument.

    """

    def get(request, location):
        nonlocal fallback, default, autoindex

        app = request.application
        response = request.response
        target = path.join(rootpath, location)

        if path.isdir(target):
            if default is True:
                default = app.settings.staticdir.default

            if not default:
                raise statuses.forbidden()

            # Default document
            targetdir = target
            target = path.join(target, default)

            # Autoindex
            if not path.exists(target) and autoindex:
                resp = index(targetdir)
                response.length = len(resp)
                response.contenttype = 'text/html'
                yield resp.encode()
                return

        # Fallback
        if not path.exists(target):
            if fallback is None:
                raise statuses.notfound()

            if not isinstance(fallback, str):
                fallback = app.settings.staticdir.fallback

            target = path.join(rootpath, fallback)
            if not path.exists(target):
                raise statuses.notfound()

        yield from _stream_file(
            request,
            target,
            path.getsize(target),
            guess_type(path.split(target)[1])[0],
        )

    return get
