.. _cookbook:

========
Cookbook
========


Query String
------------

``yhttp`` will dispatch query string to the python's ``keywordonly`` argument
if defined in handler, see ``foo`` argument in the example below.

of-course, all query string will available as a dictionary via
:attr:`req.query <yhttp.core.Request.query>`.

.. testsetup:: cookbook/qs

   from yhttp.core import Application, text
   app = Application()

.. testcode:: cookbook/qs

   @app.route()
   @text
   def get(req, *, foo=None):
       bar = req.query.get('bar')
       return f'{foo if foo else "None"} {bar if bar else "None"}'
    
   app.ready()


.. `*  due to Vim editor bug

A painless way to test our code is `bddrest
<https://github.com/pylover/bddrest>`_.

.. testcode:: cookbook/qs

   from bddrest import Given, response, when, given

   with Given(app, '/?foo=foo&bar=bar'):
       assert response.text == 'foo bar'

       when(query=given - 'foo')
       assert response.text == 'None bar'


.. _cookbook-form:

Form
----

Use :attr:`req.form <yhttp.core.Request.form>` as a dictionary to access the 
submitted fields.

.. versionchanged:: 4.0

   An easy way to get form values is:

   .. code-block::

      req.query['field-name']
      req.form['field-name']
      req.files['field-name']
      
      req.getform()['field-name']
      req.getfiles()['field-name']


.. testcode:: cookbook/form

   from yhttp.core import Application, text, statuses
   app = Application()


   @app.route()
   @text
   def post(req):
        return req.getform()['foo']


   app.ready()
   

.. testcode:: cookbook/form

   from bddrest import Given, response, when, given, status

   with Given(app, verb='POST', form={'foo': 'bar'}):
       assert status == 200
       assert response.text == 'bar'

       when(form=given - 'foo')
       assert status == 411


the ``form=`` parameter of the ``Given`` and ``when`` functions will send the
given dictionary as a ``urlencoded`` HTTP form, but you can also try 
``multipart`` content type.

.. testcode:: cookbook/form

   from bddrest import Given, response, when, given, status
   
   with Given(app, verb='POST', form={'foo': 'bar'}):
       assert status == 200
       assert response.text == 'bar'

   with Given(app, verb='POST', multipart={'foo': 'bar'}):
       assert status == 200
       assert response.text == 'bar'


.. _cookbook-settings:

Settings
--------

Use :attr:`app.settings <.Application.settings>` attribute to update global
settings instance for the application. this is an instance of 
:class:`pymlconf.Root`.

To update configuration just use the :meth:`pymlconf.Mergable.merge` or 
:meth:`pymlconf.Root.loadfile` methods of the :attr:`.Application.settings` 

Just remember configration format is yaml.

.. code-block::

   app.settings.merge('''
   db:
     url: postgres://user:pass@host/db
   ''')

   app.settings.loadfile('path/to/conf.yml')


Then use your configration keys like:

.. code-block::

   url = app.settings.db.url


.. Note::

   Do not update the :attr:`app.settings <.Application.settings>` instance
   after the :meth:`.Application.ready` is called.

.. seealso::

   `pymlconf <https://pylover.github.io/pymlconf>`_


Debug Flag
^^^^^^^^^^

You can do:

.. code-block::

   app.settings.debug = False

Or:

.. code-block::

   app.settings.merge('debug: false')  # YAML syntax


To prevent write stacktrace on error responses.

HTTP Status
-----------

There are tree ways to set HTTP status code for response: 

* use :func:`.statuscode` decorator.
* raise an instance of :class:`.statuses.HTTPStatus` class
* set :attr:`req.response.status <yhttp.core.Response.status>` directly.

These are some builtin HTTP status factory functions: 

.. currentmodule:: yhttp.core.statuses

:func:`badrequest`

:func:`unauthorized`

:func:`forbidden`

:func:`notfound`

:func:`methodnotallowed`

:func:`conflict`

:func:`gone`

:func:`preconditionfailed`

:func:`notmodified`

:func:`internalservererror`

:func:`badgateway`

:func:`movedpermanently`

:func:`found`

See the example below for usage:


.. testsetup:: cookbook/status

   from yhttp.core import Application, text
   app = Application()

.. testcode:: cookbook/status

   from yhttp.core import statuses

   @app.route()
   def get(req):
       raise statuses.notfound()
    
   app.ready()

.. testcode:: cookbook/status
   :hide:

   from bddrest import Given, status

   with Given(app):
       assert status == 404
       assert status == '404 Not Found'


This is how to use :func:`.statuscode` decorator to specify response status 
code for all requests.

.. testsetup:: cookbook/statuscode

   from yhttp.core import Application, statuscode
   app = Application()


.. testcode:: cookbook/statuscode

   from yhttp.core import statuscode

   @app.route()
   @statuscode('201 Created')
   def get(req):
       return b'Hello'
    
   app.ready()

.. testcode:: cookbook/statuscode
   :hide:

   from bddrest import Given, status

   with Given(app):
       assert status == 201


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

Or set :attr:`req.response.status <yhttp.core.Response.status>` directly.

.. code-block:: python

   @app.route()
   def get(req):
       req.response.status = '201 Created'
       return ... 


.. _cookbook-routing:

Routing
-------

the only way to register handler for http requests is
:meth:`.Application.route` decorator factory.


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

Handler function's name will be used as HTTP verb. so, the ``get`` in the 
example above stands for the HTTP ``GET`` method. 


.. _cookbook-anyverb:

Any Verb
^^^^^^^^

Another approach is to us a single star ``*`` to catch any verb.


.. code-block::

   @app.route(verb='*')          # Match any HTTP verb
   def any(req): 
       ...


.. versionadded:: 3.1


.. _cookbook-static:

Static Contents 
---------------

:class:`.Application` class has two methods: :meth:`.Application.staticfile`
and :meth:`.Application.staticdirectory` to complete this mission!


.. code-block::

   app.staticfile(r'/a\.txt', 'path/to/a.txt')
   app.staticdirectory(r'/foo/', 'path/to/foo/directory')
   app.staticdirectory(r'/foo/', 'path/to/foo/directory', default='index.txt')

.. note::

   Do not use any regular expression group inside 
   :meth:`.Application.staticdirectory`'s ``pattern`` parameter.


HTTP Cookie
-----------

This is how to use :attr:`req.cookies <yhttp.core.Request.cookies>`:

.. testsetup:: cookbook/cookie

   from yhttp.core import Application, text
   app = Application()
   app.ready()


Test:

.. testcode:: cookbook/cookie

   from http import cookies

   from bddrest import Given, response, when, given, status


   @app.route()
   def get(req):
       resp = req.response
       counter = req.cookies.get('counter')
       resp.setcookie(
           'counter',
           str(int(counter.value) + 1),
           maxage=1,
           path='/a',
           domain='example.com'
       )

   headers = {'Cookie': 'counter=1;'}
   with Given(app, headers=headers):
       assert status == 200
       assert 'Set-cookie' in response.headers
       assert response.headers['Set-cookie'] == \
           'counter=2; Domain=example.com; Max-Age=1; Path=/a'

       cookie = cookies.SimpleCookie(response.headers['Set-cookie'])
       counter = cookie['counter']
       assert counter.value == '2'
       assert counter['path'] == '/a'
       assert counter['domain'] == 'example.com'
       assert counter['max-age'] == '1'


.. _cookbook-validation:

Request Validation
------------------

``yhttp`` has a very flexible request validation system. these are some 
examples:


required
^^^^^^^^

.. testsetup:: cookbook/validation/required

   from yhttp.core import Application
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/required

   from yhttp.core import validate_form, validate_query, statuses


   @app.route()
   @validate_query(fields=dict(
       foo=dict(required=True),
   ))
   @validate_form(fields=dict(
       bar=dict(required=True),
       baz=dict(required=statuses.forbidden()),
   ))
   def post(req):
       pass

   with Given(app, verb='post', query=dict(foo='foo'), 
           form=dict(bar='bar', baz='baz')):
       assert status == 200

       when(form=given - 'bar')
       assert status == '400 Field bar is required'

       when(form=given - 'baz', query=given + dict(baz='baz'))
       assert status == '403 Forbidden'

       when(form=given - 'baz')
       assert status == '403 Forbidden'


nobody
^^^^^^

Use ``nobody`` validator when you need to prevent users to post any HTTP body
to the server.

.. testsetup:: cookbook/validation/nobody

   from yhttp.core import Application, validate_form
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/nobody

   @app.route()
   @validate_form(nobody=True)
   def foo(req):
       assert req.getform(relax=True) is None

   with Given(app, verb='foo'):
       assert status == 200

       when(form=dict(bar='baz'))
       assert status == '400 Body Not Allowed'

       when(query=dict(bar='baz'))
       assert status == 200


readonly
^^^^^^^^

``readonly`` means the field should not exists on the request form.

.. testsetup:: cookbook/validation/readonly

   from yhttp.core import Application, validate_form
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/readonly

   @app.route()
   @validate_form(fields=dict(
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

   from yhttp.core import Application, validate_form
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/regex

   @app.route()
   @validate_form(fields=dict(
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

   from yhttp.core import Application, validate_form
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/type

   @app.route()
   @validate_form(fields=dict(
       bar=dict(type_=int),
   ))
   def post(req):
       form = req.getform(relax=True)
       if form and 'bar' in form:
           assert isinstance(form['bar'], int)

   with Given(app, verb='post'):
       assert status == 200

       when(form=dict(bar='bar'))
       assert status == '400 Invalid type: `str` for field `bar`'

       when(form=dict(bar='2'))
       assert status == 200


minimum/maximum
^^^^^^^^^^^^^^^

.. testsetup:: cookbook/validation/minmax

   from yhttp.core import Application, validate_form
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/minmax
    
   @app.route()
   @validate_form(fields=dict(
       bar=dict(minlength=2, maxlength=5),
   ))
   def post(req):
       pass

   with Given(app, verb='post', form=dict(bar='123')):
       assert status == 200

       when(form=given - 'bar')
       assert status == 200

       when(form=given | dict(bar='1'))
       assert status == '400 Minimum allowed length for field bar is 2'

       when(form=given | dict(bar='123456'))
       assert status == '400 Maximum allowed length for field bar is 5'


minlength/maxlength
^^^^^^^^^^^^^^^^^^^

.. testsetup:: cookbook/validation/minmaxlength

   from yhttp.core import Application, validate_form
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/minmaxlength

   @app.route()
   @validate_form(fields=dict(
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


length
^^^^^^

.. versionadded:: 3.9.0
.. testsetup:: cookbook/validation/length

   from yhttp.core import Application, validate_form
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/length

   @app.route()
   @validate_form(fields=dict(
       bar=dict(length=6),
   ))
   def post(req):
       pass

   with Given(app, verb='post', form=dict(bar='123456')):
       assert status == 200

       when(form=given - 'bar')
       assert status == 200

       when(form=dict(bar='1'))
       assert status == '400 Allowed length for field bar is 6'

       when(form=dict(bar='12345678'))
       assert status == '400 Allowed length for field bar is 6'


Custom Callback
^^^^^^^^^^^^^^^

You can use your very own callable as the request validator:

.. testsetup:: cookbook/validation/custom

   from yhttp.core import Application, validate_form, statuses
   from bddrest import Given, when, status, given
   app = Application()

.. testcode:: cookbook/validation/custom

   from yhttp.core.validation import Field

   def customvalidator(req, value, container, field):
       assert isinstance(field, Field)
       if value[0] not in 'ab':
           raise statuses.status(400, 'Value must be either a or b')

   @app.route()
   @validate_form(fields=dict(
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
   @validate_form(fields=dict(
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


 
