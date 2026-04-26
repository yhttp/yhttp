import re
from os import path

from . import statuses


class Field:
    """Base class for all fields such as :class:`String`

    :param optional: If ``True``, the :attr:`Field.statuscode_missing` is not
                     raised when the field is not submitted by the client.
                     default: ``False``.
    :param default: A scalar or ``callable(req, field, valuesdict)`` as the
                    default value for field if not submitted. this argument
                    implies the ``optional``. default: ``None``.
    """

    statusfactory_missing = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
    the field is missing in the request.
    """

    status_contenttype = 'text/plain'
    """``contenttype`` argument of the :class:`.statuses.HTTPStatus` when
    constructing an instance with ``statusfactory_*`` factories.
    """

    def __init__(self, name, optional=False, default=None, callback=None):
        assert not (not optional and default), 'default is not accepted ' \
            'when optional is not set'

        self.name = name
        self.default = default
        self.callback = callback
        if default is not None:
            self.optional = True
        else:
            self.optional = optional

    def status_fieldmissing(self):
        return self.statusfactory_missing(
            message=f'{self.name}: Required',
            contenttype=self.status_contenttype
        )

    def __call__(self, *, optional=None, default=None, callback=None,
                 **kwargs):
        """Copy and override the field.

        .. code-block::

           bar = guard.String('bar')

           @app.route
           @app.queryguard((
               bar,
               bar(name='baz', optional=True)
           ))
           def get(req, *, bar=None, baz=None):
               ...

        """

        kwargs['optional'] = self.optional if optional is None else optional
        kwargs['default'] = self.default if default is None else default
        kwargs['callback'] = self.callback if callback is None else callback

        if 'name' not in kwargs:
            kwargs['name'] = self.name

        return self.__class__(**kwargs)

    def skip(self, req, values):
        if self.name not in values:
            if not self.optional:
                raise self.status_fieldmissing()

            if self.default is not None:
                if callable(self.default):
                    values.replace(self.name, self.default(req, self, values))
                else:
                    values.replace(self.name, self.default)

            return True

        return False

    def validate(self, req, values):
        if self.callback is None:
            return

        self.callback(req, self, values)


class String(Field):
    """Represent the guard for string field.

    :param name: str, the field name.
    :param length: ``(int, int)``, a tuple of ``(min, max)`` to specify the
                   minimum and maximum allowed length for the value.
    :param pattern: A regex pattern to specify the data format for the field.
    """

    statusfactory_badlength = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
    value length is not permitted.
    """

    statusfactory_badformat = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
    value format is not match with given pattern.
    """

    def __init__(self, name, length=None, pattern=None, **kwargs):
        self.length = length
        if pattern:
            self.pattern = re.compile(pattern)
        else:
            self.pattern = None

        super().__init__(name, **kwargs)

    def __call__(self, *, length=None, pattern=None, **kwargs):
        kwargs['length'] = self.length if length is None else length
        kwargs['pattern'] = self.pattern if pattern is None else pattern
        return super().__call__(**kwargs)

    def status_badlength(self):
        if self.length[0] == self.length[1]:
            message = f'{self.name}: Length must be {self.length[0]} ' \
                'characters'
        else:
            message = f'{self.name}: Length must be between {self.length[0]}' \
                f' and {self.length[1]} characters'

        return self.statusfactory_badlength(
            message=message,
            contenttype=self.status_contenttype
        )

    def status_badformat(self):
        return self.statusfactory_badformat(
            message=f'{self.name}: Invalid Format',
            contenttype=self.status_contenttype
        )

    def validate(self, req, values):
        if super().skip(req, values):
            return

        for i, v in enumerate(values.dict[self.name]):
            if self.length and \
                    not (self.length[0] <= len(v) <= self.length[1]):
                raise self.status_badlength()

            if self.pattern and not self.pattern.match(v):
                raise self.status_badformat()

        super().validate(req, values)


class NonStringField(Field):
    statusfactory_badtype = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
    the type cast to integer ``int(value)`` is raises :exc:`ValueError`.
    """

    def status_badtype(self, message):
        return self.statusfactory_badtype(
            message=message,
            contenttype=self.status_contenttype
        )


class Integer(NonStringField):
    """Represent the guard for integer field.

    :param name: str, the field name.
    :param range: ``(int, int)``, a tuple of ``(min, max)`` to specify the
                  minimum and maximum allowed value.
    """

    statusfactory_outofrange = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
    value is not in specified range.
    """

    def status_outofrange(self):
        return self.statusfactory_outofrange(
            message=f'{self.name}: Value must be between {self.range[0]} and '
                    f'{self.range[1]}',
            contenttype=self.status_contenttype
        )

    def __init__(self, name, range=None, **kwargs):
        self.range = range
        super().__init__(name, **kwargs)

    def __call__(self, *, range=None, **kwargs):
        kwargs['range'] = self.range if range is None else range
        return super().__call__(**kwargs)

    def validate(self, req, values):
        if super().skip(req, values):
            return

        for i, v in enumerate(values.dict[self.name]):
            try:
                v = int(v)
            except ValueError:
                raise self.status_badtype(f'{self.name}: Integer Required')

            values.dict[self.name][i] = v

            if self.range and not (self.range[0] <= v <= self.range[1]):
                raise self.status_outofrange()

        super().validate(req, values)


class Boolean(NonStringField):
    """Represent the guard for boolean field."""

    def validate(self, req, values):
        if super().skip(req, values):
            return

        for i, v in enumerate(values.dict[self.name]):
            if not v:
                raise self.status_badtype(f'{self.name}: Boolean Required')

            v = v.lower() in ('true', 'yes', 'ok', 'on')
            values.dict[self.name][i] = v

        super().validate(req, values)


class File(Field):
    """Represent the guard for multipart file field.

    It just checks the field with that name is exists in the request.

    :param name: str, the field name.
    :param extensions: list[str], allowd file extensions
    """

    statusfactory_badfileextension = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
       the received file's extension is not acceptable.
    """

    def __init__(self, name, extensions=None, length=None, pattern=None,
                 **kwargs):
        if length:
            raise NotImplementedError('length argument is not supported')

        if pattern:
            raise NotImplementedError('pattern argument is not supported')

        self.extensions = extensions
        super().__init__(name, **kwargs)

    def __call__(self, *, length=None, pattern=None, **kwargs):
        if length:
            raise NotImplementedError('length argument is not supported')

        if pattern:
            raise NotImplementedError('pattern argument is not supported')

        return super().__call__(**kwargs)

    def status_badfileextension(self):
        allowed = ', '.join(self.extensions)
        return self.statusfactory_badfileextension(
            message=f'{self.name}: invalid extension, allowed extensions: '
                    f'{allowed}',
            contenttype=self.status_contenttype
        )

    def _validate_extensions(self, file):
        _, ext = path.splitext(file.filename)
        if ext not in self.extensions:
            raise self.status_badfileextension()

    def validate(self, req, values):
        if self.name in req.getfiles():
            if self.extensions:
                self._validate_extensions(req.files[self.name])

        elif not self.optional:
            raise self.status_fieldmissing()


class Guard:
    """The :class:`.guard.Guard` class is used to validate the HTTP requests.

    see: :meth:`.Application.bodyguard` for more info.

    :param strict: If ``True``, it raises
                   :attr:`Guard.statuscode_unknownfields` when one or more
                   fields are not in the given ``fields`` argument.
    :param fields: A tuple of :class:`Gurad.Field` subclass instances to
                   define the allowed fields and field attributes.

    """
    statusfactory_unknownfields = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
    the field is not desired.
    """

    status_contenttype = 'text/plain'
    """``contenttype`` argument of the :class:`.statuses.HTTPStatus` when
    constructing an instance with ``statusfactory_*`` factories.
    """

    def status_unknownfields(self, field):
        if not isinstance(field, str):
            field = ', '.join(field)

        return self.statusfactory_unknownfields(
            message=f'Invalid field(s): {field}',
            contenttype=self.status_contenttype
        )

    def __init__(self, fields=None, strict=False):
        self.fields = {f.name: f for f in fields} if fields else fields
        self.strict = strict

    def validate(self, req, values):
        """Validates the submitted data

        :param req: Current yhttp :class:`.Request` object.
        :param values: A :class:`.MultiDict` representing the submitted data.
        """
        if self.strict:
            garbages = set(values.keys()) - set((self.fields or {}).keys())
            if garbages:
                raise self.status_unknownfields(garbages)

        if self.fields is None:
            return values

        for k, f in self.fields.items():
            f.validate(req, values)

        return values


class BodyGuard(Guard):
    """The :class:`.guard.BodyGuard` class is used to validate the HTTP
       request's body.

    see: :meth:`.Application.bodyguard` for more info.

    for other parameters and class attributes refer to :class:`.guard.Guard`
    class.

    :param contenttypes: A tuple of strings to specify allowed
                         ``content-types``.
    """

    statusfactory_invalidcontenttype = statuses.badrequest
    """A callable to create an instance of :class:`.statuses.HTTPStatus` when
    the request's content-type is not supported.
    """

    def status_invalidcontenttype(self, contenttype):
        if contenttype:
            message = f'Invalid or unsupported Content-Type: {contenttype}'
        else:
            message = 'No content-type specified'

        return self.statusfactory_invalidcontenttype(
            message=message,
            contenttype=self.status_contenttype
        )

    def __init__(self, *args, contenttypes=None, **kwargs):
        super().__init__(*args, **kwargs)
        if contenttypes is None:
            self.contenttypes = []
        elif isinstance(contenttypes, str):
            self.contenttypes = [contenttypes]
        else:
            self.contenttypes = contenttypes

    def validate(self, req, values):
        """Validates the submitted request

        :param req: Current yhttp :class:`.Request` object.
        :param values: A :class:`.MultiDict` representing the submitted data.
        """
        for ctype in self.contenttypes:
            if req.contenttype and req.contenttype.startswith(ctype):
                break

            raise self.status_invalidcontenttype(req.contenttype)

        return super().validate(req, values)
