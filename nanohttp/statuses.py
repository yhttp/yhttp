import traceback
from functools import partial


class HTTPStatus(Exception):

    def __init__(self, code, text, keepheaders=False, headers=None):
        self.keepheaders = keepheaders
        self.headers = headers or []
        self.status = f'{code} {text}'
        super().__init__(self.status)

    def setupresponse(self, response, stacktrace=False):
        response.status = self.status
        body = [self.status]
        if stacktrace:
            body.append(traceback.format_exc())

        response.body = '\r\n'.join(body)

        if not self.keepheaders:
            response.headers.clear()

        response.headers += self.headers
        response.type = 'text/plain'
        response.charset = 'utf-8'


status = HTTPStatus

badrequest = partial(status, 400, 'Bad Request')
unauthorized = partial(status, 401, 'Unauthorized')
forbidden = partial(status, 403, 'Forbidden')
notfound = partial(status, 404, 'Not Found')
methodnotallowed = partial(status, 405, 'Method Not Allowed')
conflict = partial(status, 409, 'Conflict')
gone = partial(status, 410, 'Gone')
onditionfailed = partial(status, 412, 'Precondition Failed')
notmodified = partial(status, 304, 'Not Modified')
internalservererror = partial(status, 500, 'Internal Server Error')
badgateway = partial(status, 502, 'Bad Gateway')


keepheaders = partial(status, keepheaders=True)
created = partial(keepheaders, 201, 'Created')
accepted = partial(keepheaders, 202, 'Accepted')
nocontent = partial(keepheaders, 204, 'No Content')
resetcontent = partial(keepheaders, 205, 'Reset Content')
partialcontent = partial(keepheaders, 206, 'Partial Content')


def redirect(code, text, location):
    return status(code, text, headers=[('Location', location)])


movedpermanently = partial(redirect, 301, 'Moved Permanently')
found = partial(redirect, 302, 'Found')

