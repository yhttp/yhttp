from collections import OrderedDict


class HeaderSet(OrderedDict):
    """A mutable case-insensitive ordered dictionary to keep HTTP headers.

    .. code-block::

       @app.route()
       def get(req):
           req.response.headers.add('x-foo', 'a', 'b')
           req.response.headers['x-bar'] = 'bar'
           req.response.headers += ['x-baz: qux']

    """
    def __init__(self, items=None):
        super().__init__()
        for i in items or []:
            self.add(i)

    def add(self, k, *args):
        if isinstance(k, str):
            values = []
            if ':' in k:
                k, v = k.split(':', 1)
                values += [i.strip() for i in v.split(';')]

        else:
            k, v = k
            values = [v]

        if args:
            values += args

        self[k] = '; '.join(values)

    def __getitem__(self, k):
        return super().__getitem__(k.lower())

    def __setitem__(self, k, v):
        return super().__setitem__(k.lower(), v)

    def __delitem__(self, k):
        return super().__delitem__(k)

    def __iter__(self):
        for k, v in self.items():
            yield f'{k}: {v}'

    def __str__(self):
        return '\r\n'.join(self)

    def __iadd__(self, other):
        for i in other:
            self.add(i)

        return self
