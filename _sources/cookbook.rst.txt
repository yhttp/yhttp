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

..
   cookie
   exceptions
   201 status code
   static
   routing
   validation

