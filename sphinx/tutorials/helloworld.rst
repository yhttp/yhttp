
Hello World!
============

There is how to server simple string using `yhttp`.

Create a file name: ``hello.py``:

.. testcode:: 

   from yhttp import Application

   app = Application()

   @app.route()
   def get(req):
       return b'Hello World!'

   app.ready()


.. testcode:: 
   :hide:

   from bddrest import Given, status, response

   with Given(app):
       assert status == 200
       assert response.text == 'Hello World!'

