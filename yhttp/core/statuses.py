import traceback
from functools import partial, wraps

import ujson


__all__ = [
    'HTTPStatus',
    'statuscode',
    'status',
    'ok',
    'created',
    'nocontent',
    'badrequest',
    'unauthorized',
    'forbidden',
    'notfound',
    'methodnotallowed',
    'conflict',
    'gone',
    'lengthrequired',
    'unprocessablecontent',
    'preconditionfailed',
    'notmodified',
    'internalservererror',
    'badgateway',
    'serviceunavailable',
    'gatewaytimeout',
    'movedpermanently',
    'found',
]


def _traceback(s, debug):
    body = [s.status]
    if debug:
        body.append(traceback.format_exc())

    # trailing newline
    body.append('')
    return '\r\n'.join(body)


class HTTPStatus(Exception):
    """Base class for all HTTP Exceptions.

    :param code: HTTP status code.
    :param text: HTTP status text.
    :param keepheaders: If set, appliation keeps the :attr:`.Response.headers`
                        when exception is occured.
    :param headers: Some extra HTTP headers to be added to the
                    :attr:`.Response.headers` when exception is raised.
    :param body: Additional description of what happened which will be rendered
                 inside the response body when raising this HTTP status.
                 available options:
                ``callable(status: HTTPStatus, debug: bool) -> str``,
                 ``str`` and ``None``.
                 if ``None`` specified, then no body will be rendered at all.
                 default behaviour is to render the traceback if
                 ``app.settings.debug`` is ``True``.
    :param encoder: Specify how to encode the provided body, available options:
                    ``None``, ``json`` and or a
                    ``callable(body: Any, response)`` to encode and set
                    appropriate ``response.type`` and ``response.body``.

    .. versionadded:: 7.7
       ``body`` and ``encoder`` arguments.

    """

    def __init__(self, code, text, keepheaders=False, headers=None,
                 body=_traceback, encoder=None):
        self.keepheaders = keepheaders
        self.headers = headers or []
        self.status = f'{code} {text}'
        self.body = body
        self.encoder = encoder
        super().__init__(self.status)

    def setupresponse(self, response, debug=False):
        response.status = self.status
        response.charset = 'utf-8'

        if not self.keepheaders:
            response.headers.clear()

        response.headers += self.headers

        if not self.body:
            return

        if callable(self.body):
            body = self.body(self, debug)

        else:
            body = self.body

        if not self.encoder:
            response.body = self.body
            response.type = 'text/plain'
            return

        if self.encoder == 'json':
            response.body = ujson.dumps(body)
            response.type = 'application/json'

        else:
            self.encoder(body, response)


#: Alias for :exc:`.HTTPStatus`
status = HTTPStatus

#: HTTP 200 OK
ok = partial(status, 200, 'OK', keepheaders=True)

#: HTTP 201 Created exception factory
created = partial(status, 201, 'Created', keepheaders=True)

#: HTTP 204 No Content exception factory
nocontent = partial(status, 204, 'No Content', keepheaders=True, body=None)

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

#: HTTP 411 Length Required
lengthrequired = partial(status, 411, 'Length Required')

#: HTTP 412 Precondition Failed exception factory
preconditionfailed = partial(status, 412, 'Precondition Failed')

#: HTTP 422 Unprocessable Content
unprocessablecontent = partial(status, 422, 'Unprocessable Content')

#: HTTP 304 Not Modified exception factory
notmodified = partial(status, 304, 'Not Modified', body=None)

#: HTTP 500 Internal Server Error exception factory
internalservererror = partial(status, 500, 'Internal Server Error')

#: HTTP 502 Bad Gateway exception factory
badgateway = partial(status, 502, 'Bad Gateway')

#: HTTP 503 Service Unavailable exception factory
serviceunavailable = partial(status, 503, 'Service Unavailable')

#: HTTP 504 Gateway Timeout exception factory
gatewaytimeout = partial(status, 504, 'Gateway Timeout')


def redirect(code, text, location, **kw):
    return status(code, text, keepheaders=True,
                  headers=[('Location', location)], body=None, **kw)


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
