import pytest
from bddrest import status, given, when

from yhttp import validate_form, validate_query, statuses
from yhttp.validation import TypeValidator


def test_nobody(app, Given):

    @app.route()
    @validate_form(nobody=True)
    def foo(req):
        assert req.form == {}

    with Given(verb='foo'):
        assert status == 200

        when(form=dict(bar='baz'))
        assert status == '400 Body Not Allowed'

        when(query=dict(bar='baz'))
        assert status == 200


def test_nobody_get(app, Given):

    @app.route()
    @validate_form(nobody=True)
    def get(req, *, bar=None):
        assert req.query.get('bar') == bar
        assert req.form == {}

    with Given():
        assert status == 200

        when(query=dict(bar='baz'))
        assert status == 200


def test_required(app, Given):

    err = statuses.forbidden()

    @app.route()
    @validate_form(fields=dict(
        bar=dict(required=True),
        baz=dict(required=err),
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='bar', baz='baz')):
        assert status == 200

        when(form=given - 'bar')
        assert status == '400 Field bar is required'

        when(form=given - 'baz', query=dict(baz='baz'))
        assert status == '403 Forbidden'

        when(form=given - 'baz')
        assert status == '403 Forbidden'


def test_readonly(app, Given):

    @app.route()
    @validate_form(fields=dict(
        bar=dict(readonly=True),
    ))
    def post(req):
        pass

    with Given(verb='post'):
        assert status == 200

        when(form=dict(bar='bar'))
        assert status == '400 Field bar is readonly'


def test_type(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(type_=int),
    ))
    def post(req):
        if 'bar' in req.form:
            assert isinstance(req.form['bar'], int)

    with Given(verb='post'):
        assert status == 200

        when(json=dict(bar='bar'))
        assert status == '400 Invalid type: bar'

        when(json=dict(bar='2'))
        assert status == 200


def test_ontypeerror(app, Given):
    with pytest.raises(ValueError):
        TypeValidator('str', onerror='bar')

    @app.route()
    @validate_form(fields=dict(
        bar=dict(type_=int, ontypeerror='raise'),
    ))
    def post(req):
        if 'bar' in req.form:
            assert isinstance(req.form['bar'], int)

    with Given(verb='post'):
        assert status == 200

        when(json=dict(bar='bar'))
        assert status == '400 Invalid type: bar'

        when(json=dict(bar='2'))
        assert status == '400 Invalid type: bar'

        when(json=dict(bar=2))
        assert status == 200


def test_type_querystring(app, Given):
    @app.route()
    @validate_query(fields=dict(
        bar=dict(type_=int),
    ))
    def get(req, *, bar=None):
        for i in req.query['bar']:
            assert isinstance(i, int)

        for i in bar:
            assert isinstance(i, int)

    with Given(query=dict(bar='2')):
        assert status == 200


def test_minimummaximum(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(
            minimum=2,
            maximum=9
        ),
    ))
    def post(req):
        pass

    with Given(verb='post', json=dict(bar=2)):
        assert status == 200

        when(json=dict(bar='bar'))
        assert status == '400 Minimum allowed value for field bar is 2'

        when(json=dict(bar=1))
        assert status == '400 Minimum allowed value for field bar is 2'

        when(json=dict(bar=10))
        assert status == '400 Maximum allowed value for field bar is 9'


def test_minmaxlength(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(minlength=2, maxlength=5),
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='123')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='1'))
        assert status == '400 Minimum allowed length for field bar is 2'

        when(form=given | dict(bar='123456'))
        assert status == '400 Maximum allowed length for field bar is 5'


def test_length(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(length=6),
    ))
    def post(req):
        pass

    with Given(verb='post', json=dict(bar='123456')):
        assert status == 200

        when(json=given - 'bar')
        assert status == 200

        when(json=dict(bar='1'))
        assert status == '400 Allowed length for field bar is 6'

        when(json=dict(bar='12345678'))
        assert status == '400 Allowed length for field bar is 6'


def test_regexpattern(app, Given):
    @app.route()
    @validate_form(fields=dict(
        bar=dict(pattern=r'^\d+$'),
        baz=dict(pattern=(r'\d+$', '400 Only Integer'))
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='123')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='a'))
        assert status == '400 Invalid format: bar'

        when(form=given + dict(baz='alphabet'))
        assert status == '400 Only Integer'


def test_customvalildator(app, Given):
    from yhttp.validation import Field

    def customvalidator(req, value, container, field):
        assert isinstance(field, Field)
        if value not in 'ab':
            raise statuses.status(400, 'Value must be either a or b')

    @app.route()
    @validate_form(fields=dict(
        bar=dict(callback=customvalidator)
    ))
    def post(req):
        pass

    with Given(verb='post', form=dict(bar='a')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='c'))
        assert status == '400 Value must be either a or b'

    @app.route()
    @validate_form(fields=dict(
        bar=customvalidator
    ))
    def post(req):  # noqa: W0404
        pass

    with Given(verb='post', form=dict(bar='a')):
        assert status == 200

        when(form=given - 'bar')
        assert status == 200

        when(form=given | dict(bar='c'))
        assert status == '400 Value must be either a or b'


def test_extraattribute(app, Given):

    @app.route()
    @validate_form(strict=True)
    def post(req):
        pass

    @app.route()
    @validate_form()
    def put(req):
        pass

    with Given(verb='post', form=dict(bar='123')):
        assert status == 400

        when(verb='put')
        assert status == 200

        when(form=given - 'bar')
        assert status == 200
