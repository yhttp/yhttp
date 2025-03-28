import inspect
import functools
import re
import types

import pymlconf

from . import statuses, static
from .request import Request
from .response import Response
from .cli import Main
from .guard import Guard
from .multidict import MultiDict


class BaseApplication:
    """Base application for :class:`Application` and :class:`Rewrite`
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

    def __init__(self, version=None, name=None):
        self.version = version
        self.name = name
        self.events = {}
        self.cliarguments = []
        self.settings = pymlconf.Root(self._builtinsettings)

    def when(self, func):
        """Return decorator to registers the ``func`` into :attr:`events` by
        its name.

        Currently these hooks are suuported:

        * ready
        * shutdown
        * endresponse

        The hook name will be choosed by the func.__name__, so if you need to
        aware when :meth:`ready` is called write something like this:

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
        """Only way to fire registered hooks.

        Hooks can registered by :meth:`when()` with the name.

        .. code-block::

           app.hook('endresponse')

        Extra parameters: ``*a, **kw`` will be passed to event handlers.

        Normally, users no need to call this method.
        """
        callbacks = self.events.get(name)
        if not callbacks:
            return

        for c in callbacks:
            c(*a, **kw)

    def ready(self):
        """Call the ``ready`` :meth:`hook`.

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
    """

    _builtinsettings = '''
    debug: true
    staticdir:
        autoindex: true
        default: index.html
        fallback: index.html
    '''

    routes = None
    bodyguard_factory = Guard
    queryguard_factory = Guard

    def __init__(self, version=None):
        self.routes = {}
        super().__init__(version=version)

    def _matchrequest(self, patterns, request):
        for pattern, handler, info in patterns:
            match = pattern.match(request.path)
            if not match:
                continue

            pathparams = [a for a in match.groups() if a is not None]
            query = {
                k: v for k, v in request.query.items()
                if k in info['kwonly']
            }

            return handler, pathparams, query

        return None, None, None

    def _findhandler(self, request):
        # All verbs
        patterns = self.routes.get('*', [])
        if patterns:
            handler, args, query = self._matchrequest(patterns, request)
            if handler is not None:
                return handler, args, query

        # Specific verb
        patterns = self.routes.get(request.verb.upper())
        if not patterns:
            raise statuses.methodnotallowed()

        handler, args, query = self._matchrequest(patterns, request)
        if handler is None:
            raise statuses.notfound()

        return handler, args, query

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
        response = Response(self, environ, startresponse)
        request = Request(self, environ, response)

        try:
            handler, pathparams, query = self._findhandler(request)
            body = handler(request, *pathparams, **query)

            if isinstance(body, statuses.HTTPStatus):
                raise body

            if isinstance(body, types.GeneratorType):
                response._firstchunk = next(body)

            response.body = body

        except statuses.HTTPStatus as ex:
            ex.setupresponse(response, stacktrace=self.settings.debug)

        return response.start()

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
              exists='error'):
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

        .. versionadded:: 2.9

           ``insert``

        .. versionadded:: 6.1

           ``exists``

        """
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
                        k for k, v in signature.parameters.items()
                        if v.kind == inspect.Parameter.KEYWORD_ONLY
                    }
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
        return self.route(f'{pattern}(.*)', **kw)(static.directory(
            directory,
            default,
            autoindex,
            fallback
        ))

    def bodyguard(self, fields=None, strict=False):
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
        intantiate a :class:`Guard` class or it's subclasses.

        :param fields: A tuple of :class:`Gurad.Field` subclass instances to
                       define the allowed fields and field attributes.
        :param strict: If ``True``, it raises
                       :attr:`Guard.statuscode_unknownfields` when one or more
                       fields are not in the given ``fields`` argument.
        """
        guard = self.bodyguard_factory(fields, strict)

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

    def queryguard(self, fields=None, strict=False):
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

        :param fields: A tuple of :class:`Gurad.Field` subclass instances to
                       define the allowed fields and field attributes.
        :param strict: If ``True``, it raises
                       :attr:`Guard.statuscode_unknownfields` when one or more
                       fields are not in the given ``fields`` argument.
        """
        guard = self.queryguard_factory(fields, strict)

        def decorator(handler):
            @functools.wraps(handler)
            def _handler(req, *args, **kwargs):
                if strict and (not fields) and req.query:
                    # Body not allowed
                    raise statuses.badrequest()

                req.query = guard.validate(req, req.query or MultiDict())
                return handler(req, *args, **kwargs)

            return _handler

        return decorator
