import re
import types
import inspect
import functools
import threading
import contextlib

import pymlconf

from . import statuses, static
from .request import Request
from .response import Response


class Application:
    __requestfactory__ = Request
    __responsefactory__ = Response
    threadlocal = threading.local()
    builtinsettings = '''
    debug: true
    cookie:
      http_only: false
      secure: false
    '''

    def __init__(self, **context):
        self.routes = {}
        self.events = {}
        self.settings = pymlconf.Root(self.builtinsettings, context=context)

    def _dispatch(self, verb, path):
        patterns = self.routes.get(verb)
        if not patterns:
            raise statuses.methodnotallowed()

        for pattern, func, info in patterns:
            match = pattern.match(path)
            if not match:
                continue

            kwargs = {}
            kwargs.update(match.groupdict())
            kwargs.update(
                (k, v) for k, v in self.request.query.items()
                if k in info['kwonly']
            )

            return functools.partial(
                func,
                *match.groups(),
                **kwargs,
            )

        raise statuses.notfound()

    @contextlib.contextmanager
    def _newsession(self, environ, startresponse):
        request = self.__requestfactory__(self, environ)
        response = self.__responsefactory__(self, startresponse)
        self.threadlocal.request = request
        self.threadlocal.response = response
        yield request, response
        del self.threadlocal.request
        del self.threadlocal.response

    def __call__(self, environ, startresponse):
        with self._newsession(environ, startresponse) as (request, response):
            try:
                handler = self._dispatch(request.verb, request.path)
                body = handler()
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

    def event(self, f):
        callbacks = self.events.setdefault(f.__name__, set())
        if f not in callbacks:
            callbacks.add(f)

    def hook(self, name, *a, **kw):
        callbacks = self.events.get(name)
        if not callbacks:
            return

        for c in callbacks:
            c(*a, **kw)

    @property
    def request(self):
        return self.threadlocal.request

    @property
    def response(self):
        return self.threadlocal.response

    def staticfile(self, pattern, filename):
        return self.route(pattern)(static.file(self, filename))

    def staticdirectory(self, directory):
        return self.route(r'/(.*)')(static.directory(self, directory))

