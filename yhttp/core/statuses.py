import http
import traceback
from functools import partial, wraps

import ujson


__all__ = [
    'HTTPStatus',
    'HTTPStandardStatus',
    'HTTP2xx',
    'HTTP3xx',
    'HTTP4xx',
    'HTTP5xx',
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


class HTTPStatus(Exception):
    """Base class for all HTTP statuses.

    :param code: HTTP status code.
    :param text: HTTP status text.
    :param keepheaders: If set, appliation keeps the :attr:`.Response.headers`
                        when preparing the response. otherwise, all headers
                        which set by the handler will be deleted before sending
                        the response to the client.
    :param headers: Some extra HTTP headers to be added to the
                    :attr:`.Response.headers` when preparing the response
                    regardless of the ``keepheaders`` argument.

    .. versionchanged:: 8.1
    """

    def __init__(self, code, text, headers=None, keepheaders=False):
        self.code = code
        self.text = text
        self.headers = headers
        self.keepheaders = keepheaders
        super().__init__(self.status)

    @property
    def status(self):
        return f'{self.code} {self.text}'

    def setupresponse(self, response, debug=False):
        response.status = self.status

        if not self.keepheaders:
            response.headers.clear()

        if self.headers:
            response.headers += self.headers

    def __call__(self, handler):
        """This method allows to use the instance of :class:`HTTPStatus` as a
            decorator on any yhttp handler.

        It set's the response ``status``, ``contenttype`` based on the given
        instance if no error raised.

        .. code-block::

           from yhttp.core.statuses import HTTPSTatus, nocontent


           @app.route()
           @HTTPStatus(201)
           def post(req):
               ...

           @app.route()
           @nocontent()
           def delete(req):
               ...

        .. versionadded:: 8

        """
        @wraps(handler)
        def wrapper(req, *a, **k):
            result = handler(req, *a, **k)
            req.response.status = self.status

            return result

        return wrapper


class HTTPStandardStatus(HTTPStatus):
    """Base class for all HTTP standard statuses.

    So, no need to pass the status text to constructor. it tries to find the
    propper status text from the Python's builtin :class:`http.StatusCode`
    enum. The rest of arguments are the same as the parent class:
    :class:`HTTPSTatus`.

    .. versionadded:: 8.1
    """

    #: A dictionary of ``{code: text}`` to map the status code to text.
    statustexts = {status.value: status.phrase for status in http.HTTPStatus}

    def __init__(self, code, headers=None, keepheaders=False):
        super().__init__(
            code,
            self.statustexts[code],
            headers,
            keepheaders
        )


class HTTPError(HTTPStandardStatus):
    """Represents an HTTP error.

    :param message: Description.
    :param contenttype: ``text/plain`` or ``applicatino/json``, default is
                        ``text/plain``.

    For other arguments check the parrent class: :class:`HTTPStatus`.

    .. versionadded:: 8.1
    """
    def __init__(self, *args, message=None, contenttype='text/plain', **kw):
        if contenttype not in ('text/plain', 'application/json'):
            raise ValueError(f'Content type not supported: {contenttype}')

        self.message = message
        self.contenttype = contenttype
        super().__init__(*args, keepheaders=False, **kw)

    def setupresponse(self, response, debug=False):
        super().setupresponse(response, debug)

        if self.contenttype == 'text/plain':
            body = str(self.code)
            body += ' '
            body += self.message or self.text
            body += '\r\n'
            if debug:
                body += traceback.format_exc()
                body += '\r\n'

        elif self.contenttype == 'application/json':
            body = dict(status=self.code, message=self.message)
            if debug:
                body['traceback'] = traceback.format_exc()

            body = ujson.dumps(body)

        response.charset = 'utf-8'
        response.contenttype = self.contenttype
        response.body = body


class HTTP2xx(HTTPStandardStatus):
    """Base class for all HTTP 2xx statuses.

    No body will be written when using this class or subclasses.
    """


class HTTP3xx(HTTPStandardStatus):
    """Base class for all HTTP 3xx statuses.

    No body will be written when using this class or subclasses.
    """


class HTTP4xx(HTTPError):
    """Base class for all HTTP 4xx bad request statuses."""


class HTTP5xx(HTTPError):
    """Base class for all HTTP 5xx error statuses."""
    def __init__(self, *args, error=None, **kw):
        if error:
            kw['message'] = str(error)

        super().__init__(*args, **kw)


#: HTTP 200 OK
ok = partial(HTTP2xx, 200, keepheaders=True)


#: HTTP 201 Created exception factory
created = partial(HTTP2xx, 201, keepheaders=True)


#: HTTP 204 No Content exception factory
nocontent = partial(HTTP2xx, 204, keepheaders=True)


#: HTTP 400 Bad Request exception factory
badrequest = partial(HTTP4xx, 400)


#: HTTP 401 Unauthorized exception factory
unauthorized = partial(HTTP4xx, 401)


#: HTTP 403 Forbidden exception factory
forbidden = partial(HTTP4xx, 403)


#: HTTP 404 Not Found exception factory
notfound = partial(HTTP4xx, 404)


#: HTTP 405 Method Not Allowed exception factory
methodnotallowed = partial(HTTP4xx, 405)


#: HTTP 409 Conflict exception factory
conflict = partial(HTTP4xx, 409)


#: HTTP 410 Gone exception factory
gone = partial(HTTP4xx, 410)


#: HTTP 411 Length Required
lengthrequired = partial(HTTP4xx, 411)


#: HTTP 412 Precondition Failed exception factory
preconditionfailed = partial(HTTP4xx, 412)


#: HTTP 422 Unprocessable Content
unprocessablecontent = partial(HTTP4xx, 422)


def redirect(code, location, **kw):
    return HTTP3xx(
        code,
        keepheaders=True,
        headers=[('Location', location)],
        **kw
    )


#: HTTP 301 Moved Permanently exception factory
movedpermanently = partial(redirect, 301)


#: HTTP 302 Found exception factory
found = partial(redirect, 302)


#: HTTP 304 Not Modified exception factory
notmodified = partial(HTTP3xx, 304)


#: HTTP 500 Internal Server Error exception factory
internalservererror = partial(HTTP5xx, 500)


#: HTTP 502 Bad Gateway exception factory
badgateway = partial(HTTP5xx, 502)


#: HTTP 503 Service Unavailable exception factory
serviceunavailable = partial(HTTP5xx, 503)


#: HTTP 504 Gateway Timeout exception factory
gatewaytimeout = partial(HTTP5xx, 504)
