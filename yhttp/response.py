from .headerset import HeaderSet


class Response:

    #: HTTP Status code
    status = '200 Ok'

    charset = None
    firstchunk = None
    length = None
    body = None
    type = None

    def __init__(self, app, startresponse):
        self.application = app
        self.headers = HeaderSet()
        self.startresponse = startresponse

    @property
    def contenttype(self):
        if not self.type:
            return None

        result = self.type
        if self.charset:
            result += f'; charset={self.charset}'

        return result

    def conclude(self):
        body = self.body
        if body is None:
            body = []

        elif isinstance(body, (str, bytes)):
            body = [body]

        if self.charset:
            body = [i.encode(self.charset) for i in body]

        contentlength = self.length if self.length is not None \
            else sum(len(i) for i in body)

        self.headers.add('content-length', str(contentlength))

        self.startresponse(
            self.status,
            list(self.headers.items()),
        )
        self.application.hook('endresponse', self)
        return body

    def startstream(self):
        body = self.body

        if self.length is not None:
            self.headers.add('content-length', str(self.length))

        self.startresponse(
            self.status,
            list(self.headers.items()),
        )

        # encode if required
        if self.charset and not isinstance(self.firstchunk, bytes):
            yield self.firstchunk.encode(self.charset)
            for chunk in body:
                yield chunk.encode(self.charset)

        else:
            yield self.firstchunk
            for chunk in body:
                yield chunk

        self.application.hook('endresponse')

    def start(self):
        # settingn contenttype.
        contenttype = self.contenttype
        if contenttype:
            self.headers.add('content-type', contenttype)

        if self.firstchunk is not None:
            return self.startstream()

        return self.conclude()


