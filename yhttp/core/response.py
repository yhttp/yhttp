from wsgiref.util import guess_scheme

from .headerset import HeaderSet
from .cookieset import CookieSet


class Response:
    """Represent the HTTP response.

    Which accessible by :attr:`.Request.response` inside handlers.
    """

    #: HTTP Status code
    status = '200 OK'

    #: Response encoding, ``None`` for binary
    charset = None

    #: Response content length
    length = None

    #: Response body
    body = None

    #: An instance of :class:`HeaderSet` class.
    headers = None

    #: An instance of :class:`CookieSet` class
    cookies = None

    #: Response content type without charset.
    type = None

    stream_firstchunk = None

    def __init__(self, app, environ, startresponse):
        self.application = app
        self.environ = environ
        self.startresponse = startresponse
        self.headers = HeaderSet()
        self.cookies = CookieSet()

    @property
    def contenttype(self):
        """Response content type incuding charset."""
        if not self.type:
            return None

        result = self.type
        if self.charset:
            result += f'; charset={self.charset}'

        return result

    def _compileheaders(self):
        headers = list(self.headers.items())
        if self.cookies:
            headers += self.cookies.tolist()

        return headers

    def conclude(self):
        """Conclude the response.

        Calls WSGI start_response callback and encode response body to
        transfer to the client.

        :return: response body
        """
        body = self.body
        if body is None:
            body = []

        elif isinstance(body, (str, bytes)):
            body = [body]

        if self.charset:
            body = [i.encode(self.charset) for i in body]

        contentlength = self.length if self.length is not None \
            else sum(len(i) for i in body)

        self.headers.add('content-length', str(contentlength))
        self.application.hook('startresponse', self)

        self.startresponse(self.status, self._compileheaders())
        self.application.hook('endresponse', self)
        return body

    def startstream(self):
        """Start streaming the response.

        Transfer data chunk by chunk instead of what :meth:`.conclude` does.
        """
        body = self.body

        if self.length is not None:
            self.headers.add('content-length', str(self.length))

        self.application.hook('startresponse', self)
        self.startresponse(self.status, self._compileheaders())

        # encode if required
        if self.charset and not isinstance(self.stream_firstchunk, bytes):
            yield self.stream_firstchunk.encode(self.charset)
            for chunk in body:
                yield chunk.encode(self.charset)

        else:
            yield self.stream_firstchunk
            for chunk in body:
                yield chunk

        self.application.hook('endresponse', self)

    def start(self):
        """Start the response.

        Usualy :class:`.Application` calls this method when response is ready
        to transfered to user.
        """
        contenttype = self.contenttype
        if contenttype:
            self.headers.add('content-type', contenttype)

        # Setting cookies in response headers, if any
        if self.stream_firstchunk is not None:
            return self.startstream()

        return self.conclude()

    def setcookie(self, key, value, expires=None, path=None, comment=None,
                  domain=None, maxage=None, secure=None, httponly=None,
                  samesite=None, partitioned=None):
        if secure is True:
            if guess_scheme(self.environ) != 'https':
                raise AssertionError(
                    'Cannot set secure cookie when environ[\'scheme\'] is not'
                    ' https'
                )

        self.cookies[key] = value
        entry = self.cookies[key]

        if expires:
            entry['expires'] = expires

        if path:
            entry['path'] = path

        if comment:
            entry['comment'] = comment

        if domain:
            entry['domain'] = domain

        if maxage:
            entry['max-age'] = maxage

        if secure:
            entry['secure'] = secure

        if httponly:
            entry['httponly'] = httponly

        if samesite:
            entry['samesite'] = samesite

        # TODO: will be added on python 3.14
        # if partitioned:
        #     entry['partitioned'] = partitioned

        return entry
