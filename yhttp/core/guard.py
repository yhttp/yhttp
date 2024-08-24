import re

from . import statuses


class Field:
    statuscode_missing = 400

    def __init__(self, name, optional=False, callback=None):
        self.name = name
        self.optional = optional
        self.callback = callback

    def skip(self, values):
        if self.name not in values:
            if not self.optional:
                raise statuses.status(
                    self.statuscode_missing,
                    f'{self.name}: Required'
                )

            return True

        return False

    def validate(self, req, values):
        if self.callback is None:
            return

        self.callback(req, self, values[self.name])


class String(Field):
    statuscode_badlength = 400
    statuscode_badformat = 400

    def __init__(self, name, length=None, pattern=None, **kwargs):
        self.length = length
        if pattern:
            self.pattern = re.compile(pattern)
        else:
            self.pattern = None

        super().__init__(name, **kwargs)

    def validate(self, req, values):
        if super().skip(values):
            return

        for i, v in enumerate(values.dict[self.name]):
            if self.length and \
                    not (self.length[0] <= len(v) <= self.length[1]):
                raise statuses.status(
                    self.statuscode_badlength,
                    f'{self.name}: Length must be between {self.length[0]} '
                    f'and {self.length[1]}'
                )

            if self.pattern and not self.pattern.match(v):
                raise statuses.status(
                    self.statuscode_badformat,
                    f'{self.name}: Invalid Format'
                )

        super().validate(req, values)


class Integer(Field):
    statuscode_badtype = 400
    statuscode_outofrange = 400

    def __init__(self, name, range=None, **kwargs):
        self.range = range
        super().__init__(name, **kwargs)

    def validate(self, req, values):
        if super().skip(values):
            return

        for i, v in enumerate(values.dict[self.name]):
            try:
                v = int(v)
            except ValueError:
                raise statuses.status(
                    self.statuscode_badtype,
                    f'{self.name}: Integer Required'
                )

            values.dict[self.name][i] = v

            if self.range and \
                    not (self.range[0] <= v <= self.range[1]):
                raise statuses.status(
                    self.statuscode_outofrange,
                    f'{self.name}: Value must be between {self.range[0]} and '
                    f'{self.range[1]}'
                )

        super().validate(req, values)


class Guard:
    def __init__(self, strict=False, fields=None):
        assert fields or strict, 'one of fields or strict=True must be given.'
        self.fields = {f.name: f for f in fields} if fields else fields
        self.strict = strict

    def __call__(self, req, values):
        if self.strict:
            garbages = set(values.keys()) - set((self.fields or {}).keys())
            if garbages:
                raise statuses.status(
                    400,
                    f'Invalid field(s): {", ".join(garbages)}'
                )

        if self.fields is None:
            return values

        for k, f in self.fields.items():
            f.validate(req, values)

        return values
