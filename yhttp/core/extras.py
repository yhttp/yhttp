from functools import wraps

import ujson

from . import statuses


def json_reshape(
    keep=None,
    keep_queryfield='keep-fields',
    omit=None,
    omit_queryfield='omit-fields',
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
    used. Same rule applies for omit and omit_query. However, omit and
    keep can not be used together.

    :param keep: Fields that should be kept in the response. Field names are
    separated by `,`, example: 'foo,bar'

    :param keep_query: Query parameter name that specifies the requested
    fields. set this to `None` to restrict caller from using this feature

    :param omit: Fields that should be excluded from the response, Field names
    are separated by `,`

    :param omit_query: Query parameter name that specifies the requested
    fields to be omited. set this to `None` to restrict caller from using this
    feature

    :param rename: A dictionary to determine which fields should be renamed to
    what value.
    :return: decorator for HTTP handlers
    """

    assert not (omit and keep), 'Please specify either omit or keep'

    def decorator(handler):
        @wraps(handler)
        def wrapper(req, *a, **kw):
            if keep_queryfield and omit_queryfield:

                if req.query.get(keep_queryfield) is not None \
                        and req.query.get(omit_queryfield) is not None:

                    raise statuses.status(
                        400,
                        f'Use either {keep_queryfield} or {omit_queryfield}'
                    )

            req.response.type = 'application/json'
            req.response.charset = 'utf-8'

            response = handler(req, *a, **kw)

            if rename:
                response = {rename.get(k, k): v for (k, v) in response.items()}

            field_whitelist = set(response.keys())
            field_blacklist = set()

            if omit:
                field_blacklist |= set(omit.split(','))

            if omit_query := req.query.get(omit_queryfield):
                field_blacklist |= set(omit_query.split(','))

            if keep:
                field_whitelist &= set(keep.split(','))

            if keep_query := req.query.get(keep_queryfield):
                field_whitelist &= set(keep_query.split(','))

            response = {k: v for (k, v) in response.items()
                        if k in field_whitelist and k not in field_blacklist}

            return ujson.dumps(response)

        return wrapper
    return decorator
