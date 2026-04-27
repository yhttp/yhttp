import inspect
import functools
import re
import types

import pymlconf

from . import statuses, static
from .request import Request
from .response import Response
from .cli import Main
from .guard import Guard, BodyGuard
from .multidict import MultiDict


class BaseApplication:
    """Base application for :class:`Application` and :class:`Rewrite`

    :param version: Application version
    :param name: Application name

    .. versionadded:: 6.4
       ``name`` argument.

    .. versionchanged:: 7.0
       ``version`` and ``name`` arguments must be provided to create an
       Application.

    .. versionadded:: 7.8
       ``request_factory`` and ``response_factory``

    .. versionadded:: 7.17
       ``statushandler``

    """

    _builtinsettings = '''
    debug: true
    '''

    #: Instance of :class:`pymlconf.Root` as the global configuration instance.
    settings = None

    #: A list of :class:`easycli.Argument` or :class:`easycli.SubCommand`.
    cliarguments = None

    #: A dictionary to hold registered functions to specific hooks.
    events = None

    #: A ``callable(app, environ, response)`` as the request factory
    request_factory = Request

    #: A ``callable(app, environ, startresponse)`` as the response factory
    response_factory = Response

    #: A ``callable(req, status, debug)`` to override the status response
    statushandler = None

    def __init__(self, version, name):
        self.version = version
        self.name = name
        self.events = {}
        self.cliarguments = []
        self.settings = pymlconf.Root(self._builtinsettings)

    def when(self, func):
        """Return decorator to registers the ``func`` into :attr:`events` by
        its name.

        Currently these hooks are suuported:

        * configure
        * ready
        * shutdown
        * startresponse
        * endresponse

        .. versionadded:: 7.3
           ``startresponse`` hook.

        .. versionadded:: 7.18
           ``configure`` hook.

        The hook name will be choosed by the func.__name__, so if you need to
        aware when :meth:`ready` is called write something like this:

        .. code-block::

           @app.when
           def configure(app):
               ...

           @app.when
           def ready(app):
               ...

           @app.when
           def shutdown(app):
               ...

           @app.when
           def startresponse(response):
               ...

           @app.when
           def endresponse(response):
               ...

        """
        callbacks = self.events.setdefault(func.__name__, [])
        if func not in callbacks:
            callbacks.append(func)

    def hook(self, name, *a, **kw):
        """Only way to fire registered hooks.

        Hooks can registered by :meth:`when()` by the function name.

        .. code-block::

           app.hook('endresponse')

        Extra parameters: ``*a, **kw`` will be passed to event handlers.

        Normally, users no need to call this method.
        """
        if name not in self.events:
            return

        for c in self.events.get(name):
            c(*a, **kw)

    def ready(self):
        """Call the ``configure`` and then ``ready`` application hooks.

        You need to call this method before using the instance as the WSGI
        application.

        Typical usage:

        .. code-block::

           from yhttp.core import Application, text


           app = Application()

           @app.route()
           @text
           def get(req):
               return 'Hello World!'

           if __name__ != '__main__':
               app.ready()
        """
        self.hook('configure', self)
        self.hook('ready', self)

    def shutdown(self):
        """Call the ``shutdown`` :meth:`hook`.
        """
        self.hook('shutdown', self)

    def climain(self, argv=None):
        """Provide a callable to call as the CLI entry point.

        .. code-block::

           import sys


           if __name__ == '__main__':
               sys.exit(app.climain(sys.argv))

        You can use this method as the setuptools entry point for
        `Automatic Script Creation <https://setuptools.readthedocs.io/en/la\
        test/setuptools.html#automatic-script-creation>`_

        ``setup.py``

        .. code-block::

           from setuptools import setup


           setup(
               name='foo',
               ...
               entry_points={
                   'console_scripts': [
                       'foo = foo:app.climain'
                   ]
               }
           )

        .. seealso::

           :ref:`quickstart-commandlineinterface`

        """
        return Main(self).main(argv)


class Application(BaseApplication):
    """WSGI Web Application.

    Instance of this class can be used as a WSGI application.

    :cvar bodyguard_factory: A factory of :class:`.Guard` and or it's
                             subclasses to be used in
                             :meth:`Application.bodyguard` to instantiate a new
                             guard for a handler. default: :class:`.Guard`.
    :cvar queryguard_factory: A factory of :class:`.Guard` and or it's
                              subclasses to be used in
                              :meth:`Application.queryguard` to instantiate a
                              new guard for a handler.
                              default: :class:`.Guard`.
    :ivar routes: A dictionionary to hold the regext routes handler mappings.

    :param version: Application version
    :param name: Application name
    """

    _builtinsettings = '''
    debug: true
    staticdir:
        autoindex: true
        default: index.html
        fallback: index.html
    '''

    bodyguard_factory = BodyGuard
    queryguard_factory = Guard

    def __init__(self, version, name):
        self.routes = {}
        super().__init__(version=version, name=name)

    def _matchrequest(self, patterns, request):
        for pattern, handler, info_ in patterns:
            match = pattern.match(request.path)
            if not match:
                continue

            pathparams = [a for a in match.groups() if a is not None]
            info = info_.copy()
            info['kwonly'] = {
                k: request.query[k] for k in info_['kwonly']
                if k in request.query
            }

            return handler, pathparams, info

        return None, None, None

    def _findhandler(self, request):
        # All verbs
        patterns = self.routes.get('*', [])
        if patterns:
            handler, args, info = self._matchrequest(patterns, request)
            if handler is not None:
                return handler, args, info

        # Specific verb
        patterns = self.routes.get(request.verb.upper())
        if not patterns:
            raise statuses.methodnotallowed()

        handler, args, info = self._matchrequest(patterns, request)
        if handler is None:
            raise statuses.notfound()

        trailingslash = info['trailingslash']
        if request.path.endswith('/') and trailingslash:
            if trailingslash == 'remove':
                request.path = request.path[:-1]
            else:
                raise statuses.found(request.path[:-1])

        return handler, args, info

    def __call__(self, environ, startresponse):
        """Actual WSGI Application.

        So, will be called on every request.

        .. code-block::

           from yhttp.core import Application


           app = Application()
           result = app(environ, start_response)

        Checkout the `PEP 333 <https://www.python.org/dev/peps/pep-0333/>`_
        for more info.

        """
        response = self.response_factory(self, environ, startresponse)

        try:
            request = self.request_factory(self, environ, response)
            handler, pathparams, info = self._findhandler(request)
            body = handler(request, *pathparams, **info['kwonly'])

            if isinstance(body, statuses.HTTPStatus):
                raise body

            if isinstance(body, types.GeneratorType):
                response.stream_firstchunk = next(body)

            response.body = body

        except statuses.HTTPStatus as exc:
            self.handlestatus(request, exc)
        except Exception as exc:
            self.handlestatus(request, statuses.internalservererror(
                error=exc if self.settings.debug else None
            ))

        return response.start()

    def handlestatus(self, request, status):
        if not self.statushandler or \
                not self.statushandler(request, status, self.settings.debug):
            status.setupresponse(request.response, self.settings.debug)

    def delete_route(self, pattern, verb, flags=0):
        r"""Delete a route

        :param pattern: Regular expression to match the routing table.
        :param flags: Regular expression flags. see :func:`re.compile`.
        :param verb: The HTTP verb to match the routing table.
        """
        routes = self.routes[verb.upper()]

        pat = re.compile(f'^{pattern}$', flags)
        for r in routes:
            if r[0] == pat:
                routes.remove(r)
                return

        raise ValueError(f'Route not exists: {pattern}')

    def route(self, pattern='/', flags=0, verb=None, insert=None,
              exists='error', trailingslash=None):
        r"""Return a decorator to register a handler for given regex pattern.

        if ``verb`` is ``None`` then the function name will used instead.


        .. code-block::

           @app.route(r'/.*')
           def get(req):
               ...

        You can bypass this behavior by passing ``verb`` keyword argument:

        .. code-block::

           @app.route(r'/', verb='get')
           def somethingelse(req):
               ...

        To catch any verb by the handler use ``*``.

        .. code-block::

           @app.route(r'/', verb='*')
           def any(req):
               ...

        Regular expression groups will be capture and dispatched as the
        positional arguments of the handler after ``req``:

        .. code-block::

           @app.route(r'/(\\d+)/(\\w*)')
           def get(req, id, name):
               ...

        This method returns a decorator for handler fucntions. So, you can use
        it like:

        .. code-block::

           books = app.route(r'/books/(.*)')

           @books
           def get(req, id):
               ...

           @books
           def post(req, id):
               ...

        .. seealso::

           :ref:`cookbook-routing`
           :ref:`cookbook-pathparams`


        :param pattern: Regular expression to match the request.
        :param flags: Regular expression flags. see :func:`re.compile`.
        :param verb: If not given then ``handler.__name__`` will be used to
                     match HTYP verb, Use ``*`` to catch all verbs.
        :param insert: If not given, route will be appended to the end of the
                       :attr:`routes`. Otherwise it must be an
                       integer indicating the place to insert the new route
                       into :attr:`routes` attribute.
        :param exists: Tell what to do if route already exists, possible
                       values: ``error``(default) and ``remove`` to remove the
                       existing route before appending and or inserting the new
                       one.
        :param trailingslash: String to determine the path trailing slash
                              behaviour, if ``remove``, trailing slash will be
                              removed before calling the handler.
                              if ``redirect``, handler will not called and
                              instead response with ``302 Found`` with the
                              current path wihtout the trailing slash and
                              finally if ``None``, do nothonig.

        .. versionadded:: 2.9
           ``insert``

        .. versionadded:: 6.1
           ``exists``

        .. versionadded:: 8.2
            ``trailingslash``

        """
        if trailingslash not in (None, 'redirect', 'remove'):
            raise ValueError('Invalid trailingslash argument')

        if exists not in ('error', 'remove'):
            raise ValueError('Invalid value for exists argument, use one of '
                             '`error` (the default) and or `remove`.')

        def decorator(handler):
            nonlocal verb, exists
            verbs = verb or handler.__name__

            if isinstance(verbs, str):
                verbs = [verbs]

            for verb in verbs:
                routes = self.routes.setdefault(verb.upper(), [])
                signature = inspect.signature(handler)
                info = dict(
                    kwonly={
                        k: v.default for k, v in signature.parameters.items()
                        if v.kind == inspect.Parameter.KEYWORD_ONLY
                    },
                    trailingslash=trailingslash,
                )
                pat = re.compile(f'^{pattern}$', flags)
                for r in routes:
                    if r[0] == pat:
                        if exists == 'error':
                            raise ValueError(
                                f'Route already exists: {pattern}')

                        routes.remove(r)
                        break

                route = (pat, handler, info)
                if insert is not None:
                    routes.insert(insert, route)
                else:
                    routes.append(route)

            return handler

        return decorator

    def staticfile(self, pattern, filename, **kw):
        r"""Register a filename with a regular expression pattern to be served.

        .. code-block::

            app.staticfile(r'/a\.txt', 'physical/path/to/a.txt')

        .. seealso::

           :ref:`cookbook-static`

        """
        return self.route(pattern, **kw)(static.file(filename))

    def staticdirectory(self, pattern, directory, default=None, autoindex=True,
                        fallback=None, **kw):
        r"""Register a directory with a regular expression pattern.

        So the files inside the directory are accessible by their names:

        .. code-block::

            app.staticdirectory(r'/foo/', 'physical/path/to/foo')

        You you can do:

        .. code-block:: bash

           curl localhost:8080/foo/a.txt

        .. seealso::

           :ref:`cookbook-static`

        :param pattern: Regular expression to match the requests.
        :param directory: Static files are here.
        :param default: if None, the ``app.settings.staticdir.default``
                        (which default is ``index.html``) will be used as the
                        default document.
        :param autoindex: Automatic directory indexing, default True.
        :param fallback: if ``True``, the ``app.settings.staticdir.fallback``
                        (which default is ``index.html``) will be used as the
                        fallback document if the requested resource was not
                        found. if ``str``, the value will be used instead of
                        ``app.settings.staticdir.fallback``.

        .. versionadded:: 2.13

           The *default* and *fallback* keyword arguments.

        .. versionadded:: 3.8

           The *autoindex* keyword argument.

        """
        return self.route(f'{pattern}/?(.*)', **kw)(static.directory(
            directory,
            default,
            autoindex,
            fallback
        ))

    def bodyguard(self, fields=None, strict=False, **kwargs):
        r"""A decorator factory to validate HTTP request's body.

        .. versionadded:: 5.1

        .. code-block::

           from yhttp.core import guard as g

           @app.route()
           @app.bodyguard(fields=(
               g.String('foo', length=(1, 8), pattern=r'\d+', optional=True),
               g.Integer('bar', range=(0, 9), optional=True),
           ), strict=True)
           @json()
           def post(req):
               ...

        This method calls the :attr:`bodyguard_factory` to
        intantiate a :class:`BodyGuard` class or it's subclasses.

        For list of arguments please refer to :class:`BodyGuard`.
        """
        guard = self.bodyguard_factory(fields=fields, strict=strict, **kwargs)

        def decorator(handler):
            @functools.wraps(handler)
            def _handler(req, *args, **kwargs):
                if strict and (not fields) and req.contentlength:
                    # Body not allowed
                    raise statuses.badrequest()

                req.form = guard.validate(
                    req,
                    req.getform(relax=True) or MultiDict()
                )
                return handler(req, *args, **kwargs)

            return _handler

        return decorator

    def queryguard(self, fields=None, strict=False, **kwargs):
        """A decorator factory to validate the URL's query string.

        .. versionadded:: 5.1

        .. code-block::

           from yhttp.core import guard as g
           from yhttp.core.multidict import MultiDict

           def bar(req, field: g.Field, values: MultiDict):
               return 'bar default value'

           @app.route()
           @app.queryguard(fields=(
               g.String(
                   'foo',
                   length=(1, 8),
                   pattern=r'\\d+',
                   optional=True,
                   default='foo default value',
               ),
               g.Integer(
                   'bar',
                   range=(0, 9),
                   optional=True,
                   default=bar
              ),
           ), strict=True)
           @json()
           def post(req):
               ...

        This method calls the :attr:`queryguard_factory` to
        intantiate a :class:`Guard` class or it's subclasses.

        For list of arguments please refer to :class:`Guard`.
        """
        guard = self.queryguard_factory(fields=fields, strict=strict, **kwargs)

        def decorator(handler):
            @functools.wraps(handler)
            def _handler(req, *args, **kwargs):
                if strict and (not fields) and req.query:
                    # Body not allowed
                    raise statuses.badrequest()

                req.query = guard.validate(req, req.query or MultiDict())
                for k in req.query:
                    if k in kwargs:
                        kwargs[k] = req.query[k]
                return handler(req, *args, **kwargs)

            return _handler

        return decorator
