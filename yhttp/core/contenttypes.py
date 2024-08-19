from functools import partial, wraps

import ujson

from .statuses import HTTPStatus


def contenttype(contenttype=None, charset=None, dump=None):
    r"""Yield a decorator to set response content type and encoding.

    .. code-block::

       import json

       from yhttp.core import contenttype

       @app.route()
       @contenttype('application/json', 'utf8', json.dumps)
       def get(req):
           return {'foo': 'bar'}

    There are ready to use contenttype decorators which can importes from
    ``yhttp.core`` package, like: :func:`.json`.

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
        def wrapper(req, *a, **kw):
            if contenttype:
                req.response.type = contenttype

            if charset:
                req.response.charset = charset

            try:
                body = handler(req, *a, **kw)
            except HTTPStatus as ex:
                body = ex

            if isinstance(body, HTTPStatus):
                if not body.keepheaders:
                    raise body

                return body

            if dump:
                return dump(body)

            return body

        return wrapper

    return decorator


binary = contenttype('application/octet-stream')
"""
Sets the :attr:`.Response.contenttype` to ``application/octet-stream``.

Handlers must return :class:`bytes` when this decorator is used.

.. code-block::

   from yhttp.core import binary


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

   from yhttp.core import json


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

   from yhttp.core import text


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

   from yhttp.core import html


   @app.route()
   @html
   def get(req):
       return 'Unicode String'

"""
