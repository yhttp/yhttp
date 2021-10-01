import inspect
import re
import types

import pymlconf

from . import statuses, static
from .request import Request
from .response import Response
from .cli import Main


class Application:
    """WSGI Web Application.

    Instance of this class can be used as a WSGI application.
    """

    _builtinsettings = '''
    debug: true
    staticdir:
        default: index.html
        fallback: index.html
    '''

    #: Instance of :class:`pymlconf.Root` as the global configuration instance.
    settings = None

    #: A list of :class:`easycli.Argument` or :class:`easycli.SubCommand`.
    cliarguments = None

    def __init__(self, version=None):
        self.version = version
        self.cliarguments = []
        self.routes = {}
        self.events = {}
        self.settings = pymlconf.Root(self._builtinsettings)

    def _matchrequest(self, patterns, request):
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

        return None, None, None

    def _findhandler(self, request):
        # All verbs
        patterns = self.routes.get('*', [])
        if patterns:
            func, args, query = self._matchrequest(patterns, request)
            if func is not None:
                return func, args, query

        # Specific verb
        patterns = self.routes.get(request.verb)
        if not patterns:
            raise statuses.methodnotallowed()

        func, args, query = self._matchrequest(patterns, request)
        if func is None:
            raise statuses.notfound()

        return func, args, query

    def __call__(self, environ, startresponse):
        """Actual WSGI Application.

        So, will be called on every request.

        .. code-block::

           from yhttp import Application


           app = Application()
           result = app(environ, start_response)

        Checkout the `PEP 333 <https://www.python.org/dev/peps/pep-0333/>`_
        for more info.

        """
        response = Response(self, startresponse)
        request = Request(self, environ, response)

        try:
            handler, arguments, querystrings = self._findhandler(request)
            body = handler(request, *arguments, **querystrings)
            if isinstance(body, types.GeneratorType):
                response._firstchunk = next(body)

            response.body = body

        except statuses.HTTPStatus as ex:
            ex.setupresponse(response, stacktrace=self.settings.debug)

        # Setting cookies in response headers, if any
        cookie = request.cookies.output()
        if cookie:
            for line in cookie.split('\r\n'):
                response.headers.add(line)

        return response.start()

    def route(self, pattern='/', verb=None, insert=None):
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


        :param pattern: Regular expression to match the requests.
        :param verb: If not given then ``handler.__name__`` will be used to
                     match HTYP verb, Use ``*`` to catch all verbs.
        :param insert: If not given, route will be appended to the end of the
                       :attr:`Application.routes`. Otherwise it must be an
                       integer indicating the place to insert the new route
                       into :attr:`Application.routes` attribute.

        .. versionadded:: 2.9

           ``insert``
        """

        def decorator(f):
            nonlocal verb

            verb = verb or f.__name__

            if isinstance(verb, str):
                verb = [verb]

            for verb_ in verb:
                routes = self.routes.setdefault(verb_, [])
                info = dict(
                    kwonly={
                        k for k, v in inspect.signature(f).parameters.items()
                        if v.kind == inspect.Parameter.KEYWORD_ONLY
                    }
                )
                route = (re.compile(f'^{pattern}$'), f, info)
                if insert is not None:
                    routes.insert(insert, route)
                else:
                    routes.append(route)

        return decorator

    def when(self, func):
        """Return decorator to registers the ``func`` into \
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
        """Only way to fire registered hooks.

        Hooks can registered by :meth:`.Application.when` with the name.

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

    def staticfile(self, pattern, filename, **kw):
        """Register a filename with a regular expression pattern to be served.

        .. code-block::

            app.staticfile('/a.txt', 'physical/path/to/a.txt')

        .. seealso::

           :ref:`cookbook-static`

        """
        return self.route(pattern, **kw)(static.file(filename))

    def staticdirectory(self, pattern, directory, default=None, fallback=None,
                        **kw):
        """Register a directory with a regular expression pattern.

        So the files inside the directory are accessible by their names:

        .. code-block::

            app.staticdirectory('/foo/', 'physical/path/to/foo')

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
        :param fallback: if ``True``, the ``app.settings.staticdir.fallback``
                        (which default is ``index.html``) will be used as the
                        fallback document if the requested resource was not
                        found. if ``str``, the value will be used instead of
                        ``app.settings.staticdir.fallback``.

        .. versionadded:: 2.13

           The *default* and *fallback* keyword arguments.

        """
        return self.route(f'{pattern}(.*)', **kw)(static.directory(
            directory,
            default,
            fallback
        ))

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

    def ready(self):
        """Call the ``ready`` :meth:`hook`.

        You need to call this method before using the instance as the WSGI
        application.

        Typical usage:

        .. code-block::

           from yhttp import Application, text


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
        """Call the ``shutdown`` :meth:`hook`."""
        self.hook('shutdown', self)
