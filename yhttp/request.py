import wsgiref.util as wsgiutil
from http import cookies
from urllib.parse import parse_qs, unquote, quote

import ujson

from .lazyattribute import lazyattribute
from . import statuses
from . import multipart
from . import multidict


def multipart_parse(environ):
    try:
        form, files = multipart.parse_form_data(
            environ,
            charset="utf8",
            strict=True
        )
    except multipart.MultipartError:
        raise statuses.status(400, 'Cannot parse the request')

    return form, files


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
        p = self.environ.get('PATH_INFO', '')
        p = quote(p, safe='/;=,', encoding='latin1')
        p = unquote(p)
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

        qs = parse_qs(
            self.environ['QUERY_STRING'],
            keep_blank_values=True,
            strict_parsing=True
        )

        return multidict.MultiDict(backend=qs)

    @lazyattribute
    def body(self):
        """Reads the request body.
        """
        if not self.contentlength:
            return None

        fp = self.environ.get('wsgi.input')
        if fp is None:
            raise ValueError('wsgi.input environ valriable is None')

        return fp.read(self.contentlength)

    @lazyattribute
    def json(self):
        """Return a dictionary representing the submitted JSON document.

        .. note::
            ``Content-Type`` header must be ``aplication/json``.

        .. versionadded:: 4.0
        """

        b = self.body
        if b is None:
            return None

        return ujson.decode(b)

    def getjson(self, relax=False):
        """Return the reuest body as a decoded JSON object.

        This is actualy a wrapper around the :attr:`.Request.json`. but raises
        :exc:`.statuses.lengthrequired` and
        :exc:`.statuses.unprocessablecontent` instead of programmatic
        :mod:`ujson` exceptions if ``relax=False`` (the default behaviour).

        if ``relax=True``, it returns ``None`` on any failure.
        """

        try:
            if self.json is None:
                if relax:
                    return None

                raise statuses.lengthrequired()
        except ujson.JSONDecodeError:
            if relax:
                return None

            raise statuses.unprocessablecontent()

        return self.json

    @lazyattribute
    def form(self):
        """Return a dictionary representing the submitted HTTP from.

        Parse form data from the environ dict and return a dictionary with the
        form-field name as a key(unicode) and lists as values (multiple values
        per key are possible).

        .. note::
            Both urlencoded and multipart are supported.

        .. note::
           On the first access to this attribute, the :meth:`.Request.files`
           attribute will be initialized. if any file fields are submitted
           using the ``multipart/form`` content header.

        .. versionadded:: 2.6
           An easy way to get form values is:
           .. code-block::

              req['field-name']

           The above expression is the same as:
           .. code-block::

              req.form['field-name']

        .. versionchanged:: 4.0
           The multipart files are not represented by this attribute and will
           be accessible by :meth:`.Request.files` instead.

        """
        if self.contenttype and self.contenttype in (
                'multipart/form-data'
                'application/x-www-form-urlencoded'):
            form, self.files = multipart_parse(self.environ)
            return form

        return None

    @lazyattribute
    def files(self):
        """Return a dictionary representing the submitted files.

        Parse multipart form data from the environ dict and return a
        dictionary with the form-field name as a key(unicode) and
        :class:`multipart.MultipartPart` instances as value, because the
        form-field was a file-upload or the value is too big to fit
        into memory limits.

        .. note::
           On the first access to this attribute, the :meth:`.Request.form`
           attribute will be initialized if any not-file fields are submitted.

        .. versionadded:: 4.0
        """
        if self.contenttype == 'multipart/form-data':
            self.form, files = multipart_parse(self.environ)
            return files

        return None

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
