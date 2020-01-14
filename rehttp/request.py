import wsgiref.util as wsgiutil
from http import cookies
from urllib.parse import parse_qs

from .forms import parseanyform
from .lazyattribute import lazyattribute


class Request:
    application = None

    def __init__(self, app, environ):
        self.application = app
        self.environ = environ

    @lazyattribute
    def verb(self):
        return self.environ['REQUEST_METHOD'].lower()

    @lazyattribute
    def path(self):
        return self.environ['PATH_INFO']

    @lazyattribute
    def fullpath(self):
        """Request full URI (includes query string)
        """
        return wsgiutil.request_uri(self.environ, include_query=True)

    @lazyattribute
    def contentlength(self):
        v = self.environ.get('CONTENT_LENGTH')
        return None if not v or not v.strip() else int(v)

    @lazyattribute
    def contenttype(self):
        contenttype = self.environ.get('CONTENT_TYPE')
        if contenttype:
            return contenttype.split(';')[0]
        return None

    @lazyattribute
    def query(self):
        if 'QUERY_STRING' not in self.environ:
            return {}

        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
            self.environ['QUERY_STRING'],
            keep_blank_values=True,
            strict_parsing=False
        ).items()}

    @lazyattribute
    def form(self):
        return parseanyform(
            self.environ,
            contentlength=self.contentlength,
            contenttype=self.contenttype
        )

    @lazyattribute
    def cookies(self):
        result = cookies.SimpleCookie()
        if 'HTTP_COOKIE' in self.environ:
            result.load(self.environ['HTTP_COOKIE'])
        return result

    @lazyattribute
    def scheme(self):
        """Request Scheme (http|https)
        """
        return wsgiutil.guess_scheme(self.environ)

#    def prevent_form(self, message): ## HEAD  prevent_body
#        if self.request_content_length:
#            raise exceptions.HTTPStatus(message)
#
#        self.environ['wsgi.input'] = io.BytesIO()
#

