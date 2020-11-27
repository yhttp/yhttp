from .headerset import HeaderSet


class Response:
    """Represent the HTTP response.

    Which accessible by :attr:`.Request.response` inside handlers.
    """

    #: HTTP Status code
    status = '200 Ok'

    #: Response encoding, ``None`` for binary
    charset = None

    #: Response content length
    length = None

    #: Response body
    body = None

    #: An instance of :class:`HeaderSet` class.
    headers = None

    #: Response content type without charset.
    type = None

    _firstchunk = None

    def __init__(self, app, startresponse):
        self.application = app
        self.headers = HeaderSet()
        self.startresponse = startresponse

    @property
    def contenttype(self):
        """Response content type incuding charset."""
        if not self.type:
            return None

        result = self.type
        if self.charset:
            result += f'; charset={self.charset}'

        return result

    def conclude(self):
        """Conclude the response.

        Calls WSGI start_response callback and encode response body to
        transfer to the client.

        :return: response body
        """
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
        """Start streaming the response.

        Transfer data chunk by chunk instead of what :meth:`.conclude` does.
        """
        body = self.body

        if self.length is not None:
            self.headers.add('content-length', str(self.length))

        self.startresponse(
            self.status,
            list(self.headers.items()),
        )

        # encode if required
        if self.charset and not isinstance(self._firstchunk, bytes):
            yield self._firstchunk.encode(self.charset)
            for chunk in body:
                yield chunk.encode(self.charset)

        else:
            yield self._firstchunk
            for chunk in body:
                yield chunk

        self.application.hook('endresponse', self)

    def start(self):
        """Start the response.

        Usualy :class:`.Application` calls this method when response is ready
        to transfered to user.
        """
        contenttype = self.contenttype
        if contenttype:
            self.headers.add('content-type', contenttype)

        if self._firstchunk is not None:
            return self.startstream()

        return self.conclude()
