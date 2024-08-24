import functools
import re
import abc
import warnings
from _decimal import InvalidOperation

from . import statuses


warnings.warn(
    'yhttp.core.validation module is deprecated, use yhttp.core.guard instead',
    DeprecationWarning,
    stacklevel=2
)


class Field:
    def __init__(self, title, required=None, type_=None, ontypeerror='cast',
                 minimum=None, maximum=None, length=None, minlength=None,
                 maxlength=None, callback=None, pattern=None, readonly=None):
        self.title = title
        self.criteria = []

        if readonly:
            self.criteria.append(ReadonlyValidator(readonly))

        if required:
            self.criteria.append(RequiredValidator(required))

        elif type_:
            self.criteria.append(
                TypeValidator(type_, onerror=ontypeerror)
            )

        if minimum:
            self.criteria.append(MinimumValidator(minimum))

        if maximum:
            self.criteria.append(MaximumValidator(maximum))

        if minlength:
            self.criteria.append(MinLengthValidator(minlength))

        if maxlength:
            self.criteria.append(MaxLengthValidator(maxlength))

        if length:
            self.criteria.append(LengthValidator(length))

        if pattern:
            self.criteria.append(PatternValidator(pattern))

        if callback:
            self.criteria.append(CustomValidator(callback))

    def validate(self, req, container):
        for criterion in self.criteria:
            criterion.validate(req, self, container)

        return container


class Criterion:
    statustext = None
    statuscode = 400
    exception = None

    def __init__(self, expression):
        if not isinstance(expression, tuple):
            self.expression = expression
            return

        # Expression is a tuple
        self.expression, error = expression

        if isinstance(error, str):
            parsederror = error.split(' ', 1)
            self.statuscode = int(parsederror[0])
            if len(parsederror) == 2:
                self.statustext = parsederror[1]
        else:
            self.exception = error

    def validate(self, req, field, container: dict):
        value = container.get(field.title)
        if value is None:
            return

        container[field.title] = self._validate(
            req,
            container[field.title],
            container,
            field
        )

    def _validate(self, req, value, container: dict, field):
        """Validate request.

        .. deprecated:: 5.1
           Use :mod:`.guard` instead.

        It must be overridden in the child class.

        This method should raise exception if the criterion is not met. there
        is a chance to set
        a new value because the
        container is available here.
        :param value: The value to validate
        :param field:
        :param container:
        :return:
        """
        raise NotImplementedError()

    def create_exception(self, message):
        if self.exception is not None:
            return self.exception

        statustext = self.statustext or message
        return statuses.status(self.statuscode, statustext)


class FlagCriterion(Criterion):
    def __init__(self, expression):
        if isinstance(expression, (str, statuses.HTTPStatus)):
            expression = (True, expression)

        return super().__init__(expression)


class RequiredValidator(FlagCriterion):
    def validate(self, req, field, container):
        if field.title not in container:
            raise self.create_exception(f'Field {field.title} is required')


class ReadonlyValidator(FlagCriterion):
    def validate(self, req, field, container):
        if field.title in container:
            raise self.create_exception(f'Field {field.title} is readonly')


class TypeValidator(Criterion):
    def __init__(self, *args, onerror='cast', **kw):
        super().__init__(*args, **kw)
        if onerror == 'cast':
            self._validate = self._validate_cast
        elif onerror == 'raise':
            self._validate = self._validate_raise
        else:
            raise ValueError(onerror)

    def _validate_cast(self, req, value, container, field):
        type_ = self.expression
        try:
            return type_(value)
        except (ValueError, TypeError, InvalidOperation):
            raise self.create_exception(
                f'Invalid type: `{type(field.title).__name__}` for '
                f'field `{field.title}`')

    def _validate_raise(self, req, value, container, field):
        type_ = self.expression
        if not isinstance(value, type_):
            raise self.create_exception(f'Invalid type: {field.title}')

        return value


class MinLengthValidator(Criterion):
    def _validate(self, req, value, container, field):
        if len(value) < self.expression:
            raise self.create_exception(
                f'Minimum allowed length for field {field.title} is '
                f'{self.expression}'
            )

        return value


class MaxLengthValidator(Criterion):
    def _validate(self, req, value, container, field):
        if len(value) > self.expression:
            raise self.create_exception(
                f'Maximum allowed length for field {field.title} is '
                f'{self.expression}'
            )

        return value


class LengthValidator(Criterion):
    def _validate(self, req, value, container, field):
        vlen = len(value)
        if self.expression > vlen or vlen > self.expression:
            raise self.create_exception(
                f'Allowed length for field {field.title} is '
                f'{self.expression}'
            )

        return value


class MinimumValidator(Criterion):

    def _validate(self, req, value, container, field):
        try:
            if value < self.expression:
                raise self.create_exception()
        except TypeError:
            raise self.create_exception(
                f'Minimum allowed value for field {field.title} is '
                f'{self.expression}'
            )

        return value


class MaximumValidator(Criterion):

    def _validate(self, req, value, container, field):
        try:
            if value > self.expression:
                raise self.create_exception()
        except TypeError:
            raise self.create_exception(
                f'Maximum allowed value for field {field.title} is '
                f'{self.expression}'
            )

        return value


class PatternValidator(Criterion):

    def __init__(self, pattern):
        super().__init__(pattern)
        if isinstance(self.expression, str):
            self.expression = re.compile(self.expression)

    def _validate(self, req, value, container, field):
        if self.expression.match(value) is None:
            raise self.create_exception(f'Invalid format: {field.title}')

        return value


class CustomValidator(Criterion):

    def _validate(self, req, value, container, field):
        return self.expression(req, value, container, field)


class Validator(metaclass=abc.ABCMeta):
    def __init__(self, fields=None, strict=False):
        self.strict = strict

        self.fields = {}
        if not fields:
            return

        for name, value in fields.items():
            kw = {}

            if callable(value):
                kw['callback'] = value
            else:
                kw.update(value)

            self.fields[name] = Field(name, **kw)

    def validate(self, request, form):
        if self.strict:
            extrafields = set(form.keys()) - set(self.fields.keys())
            if extrafields:
                raise statuses.status(
                    400,
                    f'Invalid field(s): {", ".join(extrafields)}'
                )

        for name, field in self.fields.items():
            field.validate(request, form)

    @abc.abstractmethod
    def __call__(self, handler):
        raise NotImplementedError


class FormValidator(Validator):
    def __init__(self, nobody=None, fields=None, strict=False):
        if nobody:
            assert fields is None, 'fields argument can\'t be used with nobody'

        self.nobody = nobody
        super().__init__(fields=fields, strict=strict)

    def __call__(self, handler):
        @functools.wraps(handler)
        def wrapper(req, *arguments, **kwargs):
            if self.nobody and req.contentlength:
                raise statuses.status(400, 'Body Not Allowed')

            self.validate(req, req.getform(relax=not self.strict) or {})
            return handler(req, *arguments, **kwargs)

        return wrapper


class QueryValidator(Validator):
    def __init__(self, fields=None, strict=False):
        super().__init__(fields=fields, strict=strict)

    def __call__(self, handler):
        @functools.wraps(handler)
        def wrapper(request, *arguments, **query):
            self.validate(request, request.query or {})
            query = {
                k: v for k, v in request.query.items()
                if k in query
            }
            return handler(request, *arguments, **query)

        return wrapper


#: see :ref:`cookbook-validation`
validate_form = FormValidator


#: see :ref:`cookbook-validation`
validate_query = QueryValidator
