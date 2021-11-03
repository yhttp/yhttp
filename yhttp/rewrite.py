import re
from urllib.parse import unquote

from .application import BaseApplication
from .response import Response
from . import statuses


class Rewrite(BaseApplication):
    r"""Useful to route specific requests to other WSGI application.

    .. versionadded:: 3.2

    .. code-block::

       import yhttp

       root = yhttp.Application()
       foo = yhttp.Application()
       bar = yhttp.Application()

       app = yhttp.Rewrite(default=root)
       app.route(r'/foo/?', r'/', foo)
       app.route(r'/bar/?(.*)', r'/b/\1', bar)
       app.ready()

       @root.route()
       def get(req):
           return 'root'

       @foo.route()
       def get(req):
           return 'foo'

       @bar.route(r'/b')
       def get(req):
           return 'bar'


    :param default: Fallback application.
    """

    def __init__(self, default=None):
        self.default = default
        self.routes = []
        super().__init__()

    def route(self, pattern, repl, handler):
        r"""Register an application for specific url.

        .. code-block::

           import yhttp

           root = yhttp.Application()
           foo = yhttp.Application()
           bar = yhttp.Application()

           app = yhttp.Rewrite(default=root)
           app.route(r'/foo/([a-z]+)/(\d+)', r'/books/\2/\1', foo)
           # Add other applications
           app.ready()

        See :py:func:`re.sub` for more info about ``pattern`` and ``repl``
        arguments.

        :param pattern: A regex pattern to match the ``environ['PATH_INFO']``.
        :param repl: URL Rewrite rule, See :py:func:`re.sub`
        :param handler: An instance of :class:`yhttp.BaseApplication`.
        """
        self.routes.append((
            re.compile(pattern),
            repl,
            handler
        ))

    def _findhandler(self, orig):
        for pattern, repl, handler in self.routes:
            new, match = pattern.subn(repl, orig)
            if not match:
                continue

            return handler, new

        return None, None

    def _notfound(self, environ, startresponse):
        response = Response(self, environ, startresponse)
        statuses.notfound().setupresponse(
            response,
            stacktrace=self.settings.debug
        )
        return response.start()

    def __call__(self, environ, startresponse):
        """Find the registred apllication, rewrite and forward the request.
        """
        pathinfo = unquote(environ['PATH_INFO'])
        handler, newurl = self._findhandler(pathinfo)

        if handler is not None:
            environ['PATH_INFO'] = newurl

        elif self.default is not None:
            handler = self.default

        else:
            return self._notfound(environ, startresponse)

        return handler(environ, startresponse)

    def ready(self):
        for _, _, app in self.routes:
            app.ready()

        if self.default is not None:
            self.default.ready()
        super().ready()

    def shutdown(self):
        for _, _, app in self.routes:
            app.shutdown()

        if self.default is not None:
            self.default.shutdown()

        super().shutdown()
