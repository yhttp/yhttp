from bddrest import status, response, given

from rehttp import validator, statuses


def test_nobody(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(nobody=True)
    def foo():
        assert app.request.form == {}

    with session(app, verb='foo'):
        assert status == 200

        when(form=dict(bar='baz'))
        assert status == '400 Body Not Allowed'


def test_required(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(fields=dict(
        bar=dict(required=True),
        baz=dict(required='700 Please provide baz'),
    ))
    def post():
        pass

    with session(
            app, verb='post', form=dict(bar='bar', baz='baz')):
        assert status == 200

        when(form=given - 'bar')
        assert status == '400 Field bar is required'

        when(form=given - 'baz', query=dict(baz='baz'))
        assert status == 200

        when(form=given - 'baz')
        assert status == '700 Please provide baz'


def test_notnone(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(fields=dict(
        bar=dict(notnone=True),
        baz=dict(notnone='700 baz cannot be null')
    ))
    def post():
        pass

    with session(app, verb='post', json=dict(bar='bar', baz='baz')):
        assert status == 200

        when(json=given - 'bar')
        assert status == 200

        when(json=given | dict(bar=None))
        assert status == '400 Field bar cannot be null'

        when(json=given - 'baz')
        assert status == 200

        when(json=given | dict(baz=None))
        assert status == '700 baz cannot be null'


def test_readonly(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(fields=dict(
        bar=dict(readonly=True),
    ))
    def post():
        pass

    with session(app, verb='post'):
        assert status == 200

        when(form=dict(bar='bar'))
        assert status == '400 Field bar is readonly'


def test_type(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(fields=dict(
        bar=dict(type_=int),
    ))
    def post():
        pass

    with session(app, verb='post'):
        assert status == 200

        when(json=dict(bar='bar'))
        assert status == '400 Invalid type: bar'


def test_minimummaximum(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(fields=dict(
        bar=dict(
            minimum=2,
            maximum=9
        ),
    ))
    def post():
        pass

    with session(app, verb='post', json=dict(bar=2)):
        assert status == 200

        when(json=dict(bar='bar'))
        assert status == '400 Minimum allowed value for field bar is 2'

        when(json=dict(bar=1))
        assert status == '400 Minimum allowed value for field bar is 2'

        when(json=dict(bar=10))
        assert status == '400 Maximum allowed value for field bar is 9'


def test_minmaxlength(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(fields=dict(
        bar=dict(minlength=2, maxlength=5),
    ))
    def post():
        pass

    with session(app, verb='post', form=dict(bar='123')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='1'))
        assert status == '400 Minimum allowed length for field bar is 2'

        when(form=given | dict(bar='123456'))
        assert status == '400 Maximum allowed length for field bar is 5'


def test_regexpattern(app, session, when):
    validate = validator(app)

    @app.route()
    @validate(fields=dict(
        bar=dict(pattern=r'^\d+$'),
    ))
    def post():
        pass

    with session(app, verb='post', form=dict(bar='123')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='a'))
        assert status == '400 Invalid format: bar'


def test_customvalildator(app, session, when):
    from rehttp.validation import Field

    validate = validator(app)

    def customvalidator(value, container, field):
        assert container is app.request.form
        assert isinstance(field, Field)
        if value not in 'ab':
            raise statuses.status(400, 'Value must be either a or b')

    @app.route()
    @validate(fields=dict(
        bar=dict(callback=customvalidator)
    ))
    def post():
        pass

    with session(app, verb='post', form=dict(bar='a')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='c'))
        assert status == '400 Value must be either a or b'

    @app.route()
    @validate(fields=dict(
        bar=customvalidator
    ))
    def post():
        pass

    with session(app, verb='post', form=dict(bar='a')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='c'))
        assert status == '400 Value must be either a or b'


