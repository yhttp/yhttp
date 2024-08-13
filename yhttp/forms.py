from urllib.parse import parse_qs

import ujson
import multipart

from . import statuses


def parseanyform(req):
    files = {}

    if req.contenttype == 'application/json':
        if req.contentlength is None:
            raise statuses.status(400, 'Content-Length required')

        fp = req.environ['wsgi.input']
        data = fp.read(req.contentlength)
        try:
            return ujson.decode(data), files
        except (ValueError, TypeError):
            raise statuses.status(400, 'Cannot parse the request')

    if req.contenttype == 'application/x-www-form-urlencoded':
        try:
            fp = req.environ['wsgi.input']
            if not fp:
                return {}, files

            fields = parse_qs(
                qs=fp.read(req.contentlength).decode(),
                keep_blank_values=True,
                strict_parsing=True,
            )
        except (TypeError, ValueError, UnicodeError):
            raise statuses.status(400, 'Cannot parse the request')

        if fields is None:
            return {}, files

        return fields, files

    if req.contenttype == 'multipart/form-data':
        try:
            fields, files = multipart.parse_form_data(
                req.environ,
                charset="utf8",
                strict=True,
            )
        except multipart.MultipartError:
            raise statuses.status(400, 'Cannot parse the request')

        return fields, files

    return {}, files
