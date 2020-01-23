========
Cookbook
========


Query String
------------

``yhttp`` will dispatch query string to the python's ``keywordonly`` argument
if defined in handler, see ``foo`` argument in the example below.

of-course, all query string will available as a dictionary via
:attr:`req.query <yhttp.Request.query>`.

.. testsetup:: cookbook/qs

   from yhttp import Application, text
   app = Application()

.. testcode:: cookbook/qs


   @app.route()
   @text
   def get(req, *, foo=None):
       return f'{foo} {req.query.get("bar")}'
    
   app.ready()

.. `*  due the vim editor bug


A painless way to test our code is `bddrest
<https://github.com/pylover/bddrest>`_.

.. testcode:: cookbook/qs

   from bddrest import Given, response, when, given

   with Given(app, '/?foo=foo&bar=bar'):
       assert response.text == 'foo bar'

       when(query=given - 'foo')
       assert response.text == 'None bar'


HTTP Form
---------

Use :attr:`req.form <yhttp.Request.form>` as a dictionary for access the submitted fields.


.. testsetup:: cookbook/form

   from yhttp import Application, text
   app = Application()

.. testcode:: cookbook/form

   @app.route()
   @text
   def post(req):
       return f'{req.form.get("foo")}'
    
   app.ready()
   

.. testcode:: cookbook/form

   from bddrest import Given, response, when, given

   with Given(app, verb='POST', form={'foo': 'bar'}):
       assert response.text == 'bar'

       when(form=given - 'foo')
       assert response.text == 'None'

the ``form=`` parameter of the ``Given`` and ``when`` functions will send the
given dictionary as a ``urlencoded`` HTTP form, but you can try ``json`` and 
``multipart`` content types to ensure all API users will happy!

.. testcode:: cookbook/form

   with Given(app, verb='POST', json={'foo': 'bar'}):
       assert response.text == 'bar'

   with Given(app, verb='POST', multipart={'foo': 'bar'}):
       assert response.text == 'bar'

HTTP Status
-----------

There are two ways for to set HTTP status code for response: raise an instance
of :class:`.HTTPStatus` class or set 
:attr:`req.response.status <yhttp.Response.status>` directly.

There are some builtins HTTP status factory functions: 

:func:`.statuses.badrequest`

:func:`.statuses.unauthorized`

:func:`.statuses.forbidden`

:func:`.statuses.notfound`

:func:`.statuses.methodnotallowed`

:func:`.statuses.conflict`

:func:`.statuses.gone`

:func:`.statuses.preconditionfailed`

:func:`.statuses.notmodified`

:func:`.statuses.internalservererror`

:func:`.statuses.badgateway`

:func:`.statuses.movedpermanently`

:func:`.statuses.found`

See the example below for usage:


.. testsetup:: cookbook/status

   from yhttp import Application, text
   app = Application()

.. testcode:: cookbook/status

   from yhttp import statuses

   @app.route()
   def get(req):
       raise statuses.notfound()
    
   app.ready()
   

.. testcode:: cookbook/status

   from bddrest import Given, when, given, status

   with Given(app):
       assert status == 404
       assert status == '404 Not Found'

HTTP Redirect
^^^^^^^^^^^^^

To redirect the request to another location raise a 
:func:`.statuses.movedpermanently` or :func:`.statuses.found`

.. code-block:: python

   raise statuses.found('http://example.com')


Custom HTTP Status
^^^^^^^^^^^^^^^^^^

Use :func:`.statuses.status` to raise your very own status code and text.

.. code-block:: python

   raise statuses.status(700, 'Custom Status Text')

Or set :attr:`req.response.status <yhttp.Response.status>` directly.

.. code-block:: python

   @app.route()
   def get(req):
       req.response.status = '201 Created'
       return ... 


Routing
-------

the only way to register handler for http requests is
:meth:`.Application.route` decorator factory.

Hanler function's name will be used as HTTP verb. so, the ``get`` in these 
example stands for the HTTP ``GET`` method.


.. code-block::

   @app.route()                 # Default route
   def get(req): 
       ...

   @app.route('/foo')           # Not match with: /foo/bar
   def get(req): 
       ...

   @app.route('/books/(\d+)')   # Match with: /books/1
   def get(req, id): 
       ...


Static Contents 
---------------

:class:`.Application` class has two methods: :meth:`.Application.staticfile`
and :meth:`.Application.staticdirectory` to complete this mission!


.. code-block::

   app.staticfile(r'/a\.txt', 'path/to/a.txt')
   app.staticdirectory(r'/foo/', 'path/to/foo/directory')

.. note::

   Do not use any regular expression group inside 
   :meth:`.Application.staticdirectory`'s ``pattern`` parameter.


HTTP Cookie
-----------

There is how to use :attr:`req.cookies <yhttp.Request.cookies>`:

.. testsetup:: cookbook/cookie

   from yhttp import Application, text
   app = Application()

.. testcode:: cookbook/cookie

   @app.route()
   def get(req):
       counter = req.cookies['counter']
       req.cookies['counter'] = str(int(counter.value) + 1)
       req.cookies['counter']['max-age'] = 1
       req.cookies['counter']['path'] = '/a'
       req.cookies['counter']['domain'] = 'example.com'
    
   app.ready()
   

Test:

.. testcode:: cookbook/cookie

   from http import cookies

   from bddrest import Given, response, when, given

   headers = {'Cookie': 'counter=1;'}
   with Given(app, headers=headers):
       assert 'Set-cookie' in response.headers
        
       cookie = cookies.SimpleCookie(response.headers['Set-cookie'])
       counter = cookie['counter']
       assert counter.value == '2'
       assert counter['path'] == '/a'
       assert counter['domain'] == 'example.com'
       assert counter['max-age'] == '1'


Request Valiation
-----------------

``yhttp`` has a very flexible request validation system. these are some 
examples:


required
^^^^^^^^

.. testsetup:: cookbook/validation/required

   from yhttp import Application
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/required

   from yhttp import validate


   @app.route()
   @validate(fields=dict(
       bar=dict(required=True),
       baz=dict(required='700 Please provide baz'),
   ))
   def post(req):
       ...

   with Given(app, verb='POST', form=dict(bar='bar', baz='baz')):
       assert status == 200

       when(form=given - 'bar')
       assert status == '400 Field bar is required'

       when(form=given - 'baz', query=dict(baz='baz'))
       assert status == 200

       when(form=given - 'baz')
       assert status == '700 Please provide baz'

notnone
^^^^^^^

.. testsetup:: cookbook/validation/notnone

   from yhttp import Application, validate
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/notnone

   @app.route()
   @validate(fields=dict(
       bar=dict(notnone=True),
       baz=dict(notnone='700 baz cannot be null')
   ))
   def post(req):
       ...

   with Given(app, verb='POST', json=dict(bar='bar', baz='baz')):
       assert status == 200

       when(json=given - 'bar')
       assert status == 200

       when(json=given | dict(bar=None))
       assert status == '400 Field bar cannot be null'

       when(json=given - 'baz')
       assert status == 200

       when(json=given | dict(baz=None))
       assert status == '700 baz cannot be null'

nobody
^^^^^^

Use ``nobody`` validator when you need to prevent users to post any HTTP body
to the server.

.. testsetup:: cookbook/validation/nobody

   from yhttp import Application, validate
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/nobody

   @app.route()
   @validate(nobody=True)
   def foo(req):
       assert req.form == {}

   with Given(app, verb='FOO'):
       assert status == 200

       when(form=dict(bar='baz'))
       assert status == '400 Body Not Allowed'


readonly
^^^^^^^^

``readonly`` means the field should not exists on the request form.

.. testsetup:: cookbook/validation/readonly

   from yhttp import Application, validate
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/readonly

   @app.route()
   @validate(fields=dict(
       bar=dict(readonly=True),
   ))
   def post(req):
       pass

   with Given(app, verb='POST'):
       assert status == 200

       when(form=dict(bar='bar'))
       assert status == '400 Field bar is readonly'


pattern
^^^^^^^

You can use regular expression to validate request fields:

.. testsetup:: cookbook/validation/regex

   from yhttp import Application, validate
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/regex

   @app.route()
   @validate(fields=dict(
       bar=dict(pattern=r'^\d+$'),
   ))
   def post(req):
       pass

   with Given(app, verb='POST', form=dict(bar='123')):
       assert status == 200

       when(form=given - 'bar')
       assert status == 200

       when(form=given | dict(bar='a'))
       assert status == '400 Invalid format: bar'


type
^^^^

Type validator gets a callable as the ``type`` and tries to cast the field's 
value by ``form[field] = type(form[field])``.

.. testsetup:: cookbook/validation/type

   from yhttp import Application, validate
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/type

   @app.route()
   @validate(fields=dict(
       bar=dict(type_=int),
   ))
   def post(req):
       pass

   with Given(app, verb='POST'):
       assert status == 200

       when(json=dict(bar='bar'))
       assert status == '400 Invalid type: bar'


minimum/maximum
^^^^^^^^^^^^^^^

.. testsetup:: cookbook/validation/minmax

   from yhttp import Application, validate
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/minmax

   @app.route()
   @validate(fields=dict(
       bar=dict(
           minimum=2,
           maximum=9
       ),
   ))
   def post(req):
       pass

   with Given(app, verb='POST', json=dict(bar=2)):
       assert status == 200

       when(json=dict(bar='bar'))
       assert status == '400 Minimum allowed value for field bar is 2'

       when(json=dict(bar=1))
       assert status == '400 Minimum allowed value for field bar is 2'

       when(json=dict(bar=10))
       assert status == '400 Maximum allowed value for field bar is 9'


minlength/maxlength
^^^^^^^^^^^^^^^^^^^

.. testsetup:: cookbook/validation/minmaxlength

   from yhttp import Application, validate
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/minmaxlength

   @app.route()
   @validate(fields=dict(
       bar=dict(minlength=2, maxlength=5),
   ))
   def post(req):
       pass

   with Given(app, verb='POST', form=dict(bar='123')):
       assert status == 200

       when(form=given - 'bar')
       assert status == 200

       when(form=given | dict(bar='1'))
       assert status == '400 Minimum allowed length for field bar is 2'

       when(form=given | dict(bar='123456'))
       assert status == '400 Maximum allowed length for field bar is 5'


custom
^^^^^^

Use can use your very own callable as the request validator:

.. testsetup:: cookbook/validation/custom

   from yhttp import Application, validate, statuses
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/custom

   from yhttp.validation import Field

   def customvalidator(value, container, field):
       assert isinstance(field, Field)
       if value not in 'ab':
           raise statuses.status(400, 'Value must be either a or b')

   @app.route()
   @validate(fields=dict(
       bar=dict(callback=customvalidator)
   ))
   def post(req):
       pass

   with Given(app, verb='POST', form=dict(bar='a')):
       assert status == 200

       when(form=given - 'bar')
       assert status == 200

       when(form=given | dict(bar='c'))
       assert status == '400 Value must be either a or b'

   @app.route()
   @validate(fields=dict(
       bar=customvalidator
   ))
   def post(req):
       pass

   with Given(app, verb='POST', form=dict(bar='a')):
       assert status == 200

       when(form=given - 'bar')
       assert status == 200

       when(form=given | dict(bar='c'))
       assert status == '400 Value must be either a or b'


 
