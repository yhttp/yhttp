import inspect
import re
import types

import pymlconf

from . import statuses, static
from .request import Request
from .response import Response
from .lazyattribute import lazyattribute
from .cli import Main


class Application:
    __requestfactory__ = Request
    __responsefactory__ = Response
    builtinsettings = '''
    debug: true
    '''

    def __init__(self):
        self.cliarguments = []
        self.routes = {}
        self.events = {}
        self.settings = pymlconf.Root(self.builtinsettings)

    def _findhandler(self, request):
        patterns = self.routes.get(request.verb)
        if not patterns:
            raise statuses.methodnotallowed()

        for pattern, func, info in patterns:
            match = pattern.match(request.path)
            if not match:
                continue

            arguments = [a for a in match.groups() if a is not None]
            querystrings = {
                k: v for k, v in request.query.items()
                if k in info['kwonly']
            }

            return func, arguments, querystrings

        raise statuses.notfound()

    def __call__(self, environ, startresponse):
        request = self.__requestfactory__(self, environ)
        request.response = response = \
            self.__responsefactory__(self, startresponse)

        try:
            handler, arguments, querystrings = self._findhandler(request)
            body = handler(request, *arguments, **querystrings)
            if isinstance(body, types.GeneratorType):
                response.firstchunk = next(body)

            response.body = body

        except statuses.HTTPStatus as ex:
            ex.setupresponse(response, stacktrace=self.settings.debug)

        # Setting cookies in response headers, if any
        cookie = request.cookies.output()
        if cookie:
            for line in cookie.split('\r\n'):
                response.headers.add(line)

        return response.start()

    def route(self, pattern='/', verb=None):
        def decorator(f):
            routes = self.routes.setdefault(verb or f.__name__, [])
            info = dict(
                kwonly={
                    k for k, v in inspect.signature(f).parameters.items()
                    if v.kind == inspect.Parameter.KEYWORD_ONLY
                }
            )
            routes.append((re.compile(f'^{pattern}$'), f, info))

        return decorator

    def when(self, f):
        callbacks = self.events.setdefault(f.__name__, [])
        if f not in callbacks:
            callbacks.append(f)

    def hook(self, name, *a, **kw):
        callbacks = self.events.get(name)
        if not callbacks:
            return

        for c in callbacks:
            c(*a, **kw)

    def staticfile(self, pattern, filename):
        return self.route(pattern)(static.file(filename))

    def staticdirectory(self, directory):
        return self.route(r'/(.*)')(static.directory(directory))

    def climain(self, argv=None):
        """Provide a callable to call as the CLI entry point
        """
        return Main(self).main(argv)

    def ready(self):
        self.hook('ready', self)

    def shutdown(self):
        self.hook('shutdown', self)

