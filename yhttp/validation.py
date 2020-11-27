import functools
import re
from _decimal import InvalidOperation

from . import statuses


class Field:
    def __init__(self, title, required=None, type_=None, minimum=None,
                 maximum=None, pattern=None, minlength=None, maxlength=None,
                 callback=None, notnone=None, readonly=None):
        self.title = title
        self.criteria = []

        if readonly:
            self.criteria.append(ReadonlyValidator(readonly))

        if required:
            self.criteria.append(RequiredValidator(required))

        if notnone:
            self.criteria.append(NotNoneValidator(notnone))

        if type_:
            self.criteria.append(TypeValidator(type_))

        if minimum:
            self.criteria.append(MinimumValidator(minimum))

        if maximum:
            self.criteria.append(MaximumValidator(maximum))

        if minlength:
            self.criteria.append(MinLengthValidator(minlength))

        if maxlength:
            self.criteria.append(MaxLengthValidator(maxlength))

        if pattern:
            self.criteria.append(PatternValidator(pattern))

        if callback:
            self.criteria.append(CustomValidator(callback))

    def validate(self, container):
        for criterion in self.criteria:
            criterion.validate(self, container)

        return container


class Criterion:
    statustext = None
    statuscode = 400

    def __init__(self, expression):
        if not isinstance(expression, tuple):
            self.expression = expression
            return

        # Expression is a tuple
        self.expression, error = expression

        parsederror = error.split(' ', 1)
        self.statuscode = int(parsederror[0])

        if len(parsederror) == 2:
            self.statustext = parsederror[1]

    def validate(self, field: Field, container: dict):
        value = container.get(field.title)
        if value is None:
            return

        container[field.title] = self._validate(
            container[field.title],
            container,
            field
        )

    def _validate(self, value, container: dict, field: Field
                  ):  # pragma: no cover
        """Validate request.

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
        statustext = self.statustext or message
        return statuses.status(self.statuscode, statustext)


class FlagCriterion(Criterion):
    def __init__(self, expression):
        if isinstance(expression, str):
            expression = (True, expression)

        return super().__init__(expression)


class RequiredValidator(FlagCriterion):
    def validate(self, field, container):
        if field.title not in container:
            raise self.create_exception(f'Field {field.title} is required')


class NotNoneValidator(FlagCriterion):
    def validate(self, field, container):
        if field.title not in container:
            return

        if container[field.title] is None:
            raise self.create_exception(f'Field {field.title} cannot be null')


class ReadonlyValidator(FlagCriterion):
    def validate(self, field, container):
        if field.title in container:
            raise self.create_exception(f'Field {field.title} is readonly')


class TypeValidator(Criterion):

    def _validate(self, value, container, field):
        type_ = self.expression
        try:
            return type_(value)
        except (ValueError, TypeError, InvalidOperation):
            raise self.create_exception(f'Invalid type: {field.title}')


class MinLengthValidator(Criterion):

    def _validate(self, value, container, field):
        if len(value) < self.expression:
            raise self.create_exception(
                f'Minimum allowed length for field {field.title} is '
                f'{self.expression}'
            )

        return value


class MaxLengthValidator(Criterion):

    def _validate(self, value, container, field):
        if len(value) > self.expression:
            raise self.create_exception(
                f'Maximum allowed length for field {field.title} is '
                f'{self.expression}'
            )

        return value


class MinimumValidator(Criterion):

    def _validate(self, value, container, field):
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

    def _validate(self, value, container, field):
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

    def _validate(self, value, container, field):
        if self.expression.match(value) is None:
            raise self.create_exception(f'Invalid format: {field.title}')

        return value


class CustomValidator(Criterion):

    def _validate(self, value, container, field):
        return self.expression(value, container, field)


class RequestValidator:
    def __init__(self, nobody=None, fields=None):
        self.nobody = nobody

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

    def validate(self, request):

        if self.nobody and request.form:
            raise statuses.status(400, 'Body Not Allowed')

        for name, field in self.fields.items():

            if request.query and name in request.query:
                field.validate(request.query)

            else:
                field.validate(request.form)

    def __call__(self, handler):

        @functools.wraps(handler)
        def wrapper(request, *a, **kw):
            self.validate(request)
            return handler(request, *a, **kw)

        return wrapper


#: see :ref:`cookbook-validation`
validate = RequestValidator
