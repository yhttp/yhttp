from functools import partial, wraps

import ujson


def contenttype(app, contenttype=None, charset=None, dump=None):
    def decorator(handler):
        @wraps(handler)
        def wrapper(request, response, *a, **kw):
            if contenttype:
                response.type = contenttype

            if charset:
                app.response.charset = charset

            body = handler(request, response, *a, **kw)
            return dump(body) if dump else body

        return wrapper

    return decorator


binary = partial(contenttype, contenttype='application/octet-stream')
utf8 = partial(contenttype, charset='utf-8')
json = partial(utf8, contenttype='application/json', dump=ujson.dumps)
text = partial(utf8, contenttype='text/plain')

