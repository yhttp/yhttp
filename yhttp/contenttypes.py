from functools import partial, wraps

import ujson


def contenttype(contenttype=None, charset=None, dump=None):
    r"""Yield a decorator to set response content type and encoding.

    .. code-block::

       import json

       from yhttp import contenttype

       @app.route()
       @contenttype('application/json', 'utf8', json.dumps)
       def get(req):
           return {'foo': 'bar'}

    There are ready to use contenttype decorators which can importes from
    ``yhttp`` package, like: :func:`.json`.

    You may create your very own content type decorator by calling this
    function with desired arguments, for example:

    .. code-block::

       invoice = contenttype('application/pdf', None, dump=makeinvoicepdf)

       @app.route('/invoices/(\d+)')
       @invoice
       def get(req, id):
           ...

    The :func:`.json` decorator is created with something like:

    .. code-block::

       json = contenttype('application/json', 'utf8', dump=json.dumps)

    .. seealso::

       :func:`.binary`
       :func:`.json`
       :func:`.text`

    :param contenttype: HTTP Content-Type, example: application/json
    :param charset: Character set, example: utf8
    :param dump: A ``callable(body) -> body`` to transform the body to
                 appropriate content type.
    :return: decorator for HTTP handlers.
    """

    def decorator(handler):
        @wraps(handler)
        def wrapper(request, *a, **kw):
            if contenttype:
                request.response.type = contenttype

            if charset:
                request.response.charset = charset

            body = handler(request, *a, **kw)
            return dump(body) if dump else body

        return wrapper

    return decorator


binary = contenttype('application/octet-stream')
"""
Sets the :attr:`.Response.contenttype` to ``application/octet-stream``.

Handlers must return :class:`bytes` when this decorator is used.

.. code-block::

   from yhttp import binary


   @app.route()
   @binary
   def get(req):
       return b'binarydata'

"""

utf8 = partial(contenttype, charset='utf-8')


json = utf8('application/json', dump=ujson.dumps)
"""
Sets the :attr:`.Response.contenttype` to ``application/json;charset=utf-8``
and encode the returned value by handler to json byte-string format.

Handlers must return :class:`dict` when this decorator is used.

.. code-block::

   from yhttp import json


   @app.route()
   @json
   def get(req):
       return {'foo': 'bar'}

"""


text = utf8('text/plain')
"""
Sets the :attr:`.Response.contenttype` to ``text/text; charset=utf-8``.

Handlers must return :class:`str` when this decorator is used.

.. versionadded:: 2.8

.. code-block::

   from yhttp import text


   @app.route()
   @text
   def get(req):
       return 'Unicode String'

"""


html = utf8('text/html')
"""
Sets the :attr:`.Response.contenttype` to ``text/html; charset=utf-8``.

Handlers must return :class:`str` when this decorator is used.

.. versionadded:: 2.8

.. code-block::

   from yhttp import html


   @app.route()
   @html
   def get(req):
       return 'Unicode String'

"""
