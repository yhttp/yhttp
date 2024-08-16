from collections.abc import MutableMapping


class MultiDict(MutableMapping):
    """ A dict that remembers old values for each key.

    HTTP headers and query strings may repeat with differing values, such as
    Set-Cookie. We need to remember all values.
    """

    def __init__(self, backend=None, *args, **kwargs):
        self.dict = backend if backend is not None else dict()

        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def __delitem__(self, key):
        del self.dict[key]

    def keys(self):
        return self.dict.keys()

    def __getitem__(self, key):
        return self.get(key, KeyError, -1)

    def __setitem__(self, key, value):
        self.append(key, value)

    def append(self, key, value):
        self.dict.setdefault(key, []).append(value)

    def replace(self, key, value):
        self.dict[key] = [value]

    def getall(self, key):
        return self.dict.get(key) or []

    def get(self, key, default=None, index=-1):
        if key not in self.dict and default != KeyError:
            return [default][index]

        return self.dict[key][index]

    def iterallitems(self):
        for key, values in self.dict.items():
            for value in values:
                yield key, value
