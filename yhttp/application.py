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
        """The actual WSGI Application.

        So, will be called on every request.
        """
        request = Request(self, environ)
        request.response = response = Response(self, startresponse)

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
        """Decorator factory to register a handler for given regex pattern.
        if ``verb`` is ``None`` then the function name will used instead.

        .. code-block::

           @app.route(r'/.*')
           def get(req):
               ...

        Regular expression groups will be capture and dispatched as the
        positional arguments of the handler afet ``req``:

        .. code-block::

           @app.route(r'/(\d+)/(\w*)')
           def get(req, id, name):
               ...

        This method returns a decorator for handler fucntions. So, you can use
        it like:

        .. code-block::

           books = app.route(s'/books/(.*)')

           @books
           def get(req, id):
               ...

           @books
           def post(req, id):
               ...

        :param pattern: Regular expression to match the requests.
        """

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

    def when(self, func):
        """A Decorator to registers the ``func`` into
        :attr:`.Application.events` by its name.

        Currently these hooks are suuported:

        * ready
        * shutdown
        * endresponse

        The hook name will be choosed by the func.__name__, so if you need to
        aware when ``app.ready`` is called write something like this:

        .. code-block::

           @app.when
           def ready(app):
               ...

           @app.when
           def shutdown(app):
               ...

           @app.when
           def endresponse(response):
               ...

        """

        callbacks = self.events.setdefault(func.__name__, [])
        if func not in callbacks:
            callbacks.append(func)

    def hook(self, name, *a, **kw):
        callbacks = self.events.get(name)
        if not callbacks:
            return

        for c in callbacks:
            c(*a, **kw)

    def staticfile(self, pattern, filename):
        return self.route(pattern)(static.file(filename))

    def staticdirectory(self, pattern, directory):
        return self.route(f'{pattern}(.*)')(static.directory(directory))

    def climain(self, argv=None):
        """Provide a callable to call as the CLI entry point
        """
        return Main(self).main(argv)

    def ready(self):
        self.hook('ready', self)

    def shutdown(self):
        self.hook('shutdown', self)

