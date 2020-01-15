from functools import partial, wraps

import ujson


def contenttype(contenttype=None, charset=None, dump=None):
    def decorator(handler):
        @wraps(handler)
        def wrapper(request, *a, **kw):
            if contenttype:
                request.response.type = contenttype

            if charset:
                request.response.charset = charset

            body = handler(request, *a, **kw)
            return dump(body) if dump else body

        return wrapper

    return decorator


binary = contenttype('application/octet-stream')
utf8 = partial(contenttype, charset='utf-8')
json = utf8('application/json', dump=ujson.dumps)
text = utf8('text/plain')

