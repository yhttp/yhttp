
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


.. testcode:: 
   :hide:

   from bddrest import Given
