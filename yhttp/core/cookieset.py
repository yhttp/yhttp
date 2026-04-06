from http.cookies import SimpleCookie


class CookieSet(SimpleCookie):
    """
    CookieSet class just extends the :class:`http.cookies.SimpleCookie` class
    to create a list of HTTP headers, because the
    class:`http.cookies.SimpleCookie` class just outputs a
    concatenated strings.

    .. versionadded:: 7.16
    """

    def tolist(self, attrs=None, header='Set-Cookie:'):
        """Return a header list suitable for WSGI start_response function."""
        result = []
        for key, value in sorted(self.items()):
            result.append(value.output(attrs, header))

        return result
