from functools import wraps

import ujson

from . import statuses


def json_reshape(
    keep=None,
    keep_queryfield='keep-fields',
    ommit=None,
    ommit_queryfield='ommit-fields',
    rename=None
):
    """
    reshapes the json response of the API

    Handlers must return :class:`jsonable` when this decorator is used.

    .. code-block::

       from yhttp.core import json


       @app.route()
       @json_reshape(keep_query='keep-fields')
       def get(req):
           return {'foo': 'bar'}


    keep and keep_query, can be used together and their intersection will be
    used. Same rule applies for ommit and ommit_query. However, ommit and
    keep can not be used together.

    :param keep: Fields that should be kept in the response. Field names are
    separated by `,`, example: 'foo,bar'

    :param keep_query: Query parameter name that specifies the requested
    fields. set this to `None` to restrict caller from using this feature

    :param ommit: Fields that should be excluded from the response, Field names
    are separated by `,`

    :param ommit_query: Query parameter name that specifies the requested
    fields to be ommited. set this to `None` to restrict caller from using this
    feature

    :param rename: A dictionary to determine which fields should be renamed to
    what value.
    :return: decorator for HTTP handlers
    """

    assert not (ommit and keep), 'Please specify either ommit or keep'

    def decorator(handler):
        @wraps(handler)
        def wrapper(req, *a, **kw):
            if keep_queryfield and ommit_queryfield:

                if req.query.get(keep_queryfield) is not None \
                        and req.query.get(ommit_queryfield) is not None:

                    raise statuses.status(
                        400,
                        f'Use either {keep_queryfield} or {ommit_queryfield}'
                    )

            req.response.type = 'application/json'
            req.response.charset = 'utf-8'

            response = handler(req, *a, **kw)

            field_whitelist = set(response.keys())
            field_blacklist = set()

            if ommit:
                field_blacklist.update(ommit.split(','))

            if ommit_query := req.query.get(ommit_queryfield):
                field_blacklist.update(ommit_query.split(','))

            response = {k: v for (k, v) in response.items()
                        if k in field_whitelist and k not in field_blacklist}
            return ujson.dumps(response)

        return wrapper
    return decorator
