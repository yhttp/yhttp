import wsgiref.util as wsgiutil
from http import cookies
from urllib.parse import parse_qs

from .forms import parseanyform
from .lazyattribute import lazyattribute


class Request:
    """Represent an HTTP request.

    :meth:`.Application.__call__` instantiates this class on each call.
    """

    application = None

    #: The :class:`.Response` instance associated to this request.
    response = None

    #: WSIG environ dictionary
    environ = None

    def __init__(self, app, environ, response):
        self.application = app
        self.environ = environ
        self.response = response

    @lazyattribute
    def verb(self):
        """HTTP method."""
        return self.environ['REQUEST_METHOD'].lower()

    @lazyattribute
    def path(self):
        """Request URL without query string and ``scheme://domain.ext``."""
        p = self.environ['PATH_INFO']
        if not p.startswith('/'):
            return f'/{p}'

        return p

    @lazyattribute
    def fullpath(self):
        """Request full URI including query string."""
        return wsgiutil.request_uri(self.environ, include_query=True)

    @lazyattribute
    def contentlength(self):
        """HTTP Request ``Content-Length`` header value."""
        v = self.environ.get('CONTENT_LENGTH')
        return None if not v or not v.strip() else int(v)

    @lazyattribute
    def contenttype(self):
        """HTTP Request ``Content-Type`` header value without encoding."""
        contenttype = self.environ.get('CONTENT_TYPE')
        if contenttype:
            return contenttype.split(';')[0]
        return None

    @lazyattribute
    def query(self):
        """Return A dictionary representing the submitted query string."""
        if 'QUERY_STRING' not in self.environ:
            return {}

        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
            self.environ['QUERY_STRING'],
            keep_blank_values=True,
            strict_parsing=False
        ).items()}

    @lazyattribute
    def form(self):
        """Return dictionary representing the submitted from.

        Currently, json, urlencoded and multipart form are supported.

        .. versionadded:: 2.6

           An easy way to get form values is:

           .. code-block::

              req['field-name']

           The above expression is the same as:

           .. code-block::

              req.form['field-name']


        """
        return parseanyform(
            self.environ,
            contentlength=self.contentlength,
            contenttype=self.contenttype
        )

    @lazyattribute
    def cookies(self):
        """Return a dictionary representing the HTTP cookie data."""
        result = cookies.SimpleCookie()
        if 'COOKIE' in self.headers:
            result.load(self.headers['COOKIE'])
        return result

    @lazyattribute
    def scheme(self):
        """Return HTTP Request Scheme (http|https)."""
        return wsgiutil.guess_scheme(self.environ)

    @lazyattribute
    def headers(self):
        """HTTP Request headers set.

        see :class:`.HeadersMask` class to figure out how it works.
        """
        return HeadersMask(self.environ)

    def __getitem__(self, field):
        return self.form[field]


class HeadersMask:
    """A simple proxy over :attr:`.Request.environ`.

    Useful to get headers by their original name without the ``HTTP_`` prefix,
    which is the python's WSGI servers default behavior.

    .. code-block::

       @app.route()
       def get(req):
           foo = req.headers['foo']
           bar = req.headers.get('bar')
           if 'baz' in req.headers:
               baz = True

            ...

    """

    def __init__(self, environ):
        self.environ = environ

    @staticmethod
    def getkey(k):
        return f'HTTP_{k.replace("-", "_").upper()}'

    def __getitem__(self, key):
        return self.environ[self.getkey(key)]

    def get(self, key, default=None):
        return self.environ.get(self.getkey(key), default)

    def __contains__(self, key):
        return self.getkey(key) in self.environ
