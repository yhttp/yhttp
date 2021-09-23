import traceback
from functools import partial, wraps


class HTTPStatus(Exception):
    """Base class for all HTTP Exceptions.

    :param code: HTTP status code.
    :param text: HTTP status text.
    :param keepheaders: If set, appliation keeps the :attr:`.Response.headers`
                        when exception is occured.
    :param headers: Some extra HTTP headers to be added to the
                    :attr:`.Response.headers` when exception is raised.
    """

    def __init__(self, code, text, keepheaders=False, headers=None,
                 nobody=False):
        self.keepheaders = keepheaders
        self.headers = headers or []
        self.status = f'{code} {text}'
        self.nobody = nobody
        super().__init__(self.status)

    def setupresponse(self, response, stacktrace=False):
        response.status = self.status
        if not self.nobody:
            body = [self.status]
            if stacktrace:
                body.append(traceback.format_exc())

            response.body = '\r\n'.join(body)

        if not self.keepheaders:
            response.headers.clear()

        response.headers += self.headers
        response.type = 'text/plain'
        response.charset = 'utf-8'


#: Alias for :class:`.HTTPStatus`
status = HTTPStatus

ok = partial(status, keepheaders=True)

#: HTTP 201 Created exception factory
nocontent = partial(ok, 201, 'Created')

#: HTTP 204 No Content exception factory
nocontent = partial(ok, 204, 'No Content', nobody=True)

#: HTTP 400 Bad Request exception factory
badrequest = partial(status, 400, 'Bad Request')

#: HTTP 401 Unauthorized exception factory
unauthorized = partial(status, 401, 'Unauthorized')

#: HTTP 403 Forbidden exception factory
forbidden = partial(status, 403, 'Forbidden')

#: HTTP 404 Not Found exception factory
notfound = partial(status, 404, 'Not Found')

#: HTTP 405 Method Not Allowed exception factory
methodnotallowed = partial(status, 405, 'Method Not Allowed')

#: HTTP 409 Conflict exception factory
conflict = partial(status, 409, 'Conflict')

#: HTTP 410 Gone exception factory
gone = partial(status, 410, 'Gone')

#: HTTP 412 Precondition Failed exception factory
preconditionfailed = partial(status, 412, 'Precondition Failed')

#: HTTP 304 Not Modified exception factory
notmodified = partial(status, 304, 'Not Modified', nobody=True)

#: HTTP 500 Internal Server Error exception factory
internalservererror = partial(status, 500, 'Internal Server Error')

#: HTTP 502 Bad Gateway exception factory
badgateway = partial(status, 502, 'Bad Gateway')


def redirect(code, text, location):
    return status(code, text, headers=[('Location', location)], nobody=True)


#: HTTP 301 Moved Permanently exception factory
movedpermanently = partial(redirect, 301, 'Moved Permanently')


#: HTTP 302 Found exception factory
found = partial(redirect, 302, 'Found')


def statuscode(code):
    """Set the :attr:`.Response.status` to ``code``.

    .. code-block::

       @app.route()
       @statuscode('201 Created')
       def post(req):
           ...

       with Given(app, verb='POST'):
           assert status == '201 Created'

    .. versionadded:: 2.5

    """
    def decorator(handler):
        @wraps(handler)
        def wrapper(req, *a, **k):
            result = handler(req, *a, **k)
            req.response.status = code if isinstance(code, str) else \
                code().status

            return result

        return wrapper

    return decorator
