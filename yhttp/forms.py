import cgi

import ujson

from . import statuses


def getcgifieldvalue(field):
    return field.value \
        if isinstance(field, cgi.MiniFieldStorage) \
        or (
            isinstance(field, cgi.FieldStorage)
            and not field._binary_file
        ) \
        else field


def parseanyform(environ, contentlength=None, contenttype=None):
    if contenttype == 'application/json':
        if contentlength is None:
            raise statuses.status(400, 'Content-Length required')

        fp = environ['wsgi.input']
        data = fp.read(contentlength)
        try:
            return ujson.decode(data)
        except (ValueError, TypeError):
            raise statuses.status(400, 'Cannot parse the request')

    if 'QUERY_STRING' not in environ:
        environ['QUERY_STRING'] = ''

    try:
        storage = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            strict_parsing=False,
            keep_blank_values=True
        )
    except (TypeError, ValueError):
        raise statuses.status(400, 'Cannot parse the request')

    result = {}
    if storage.list is None or not len(storage.list):
        return result

    for k in storage:
        v = storage[k]

        if isinstance(v, list):
            result[k] = [getcgifieldvalue(i) for i in v]
        else:
            result[k] = getcgifieldvalue(v)

    return result
