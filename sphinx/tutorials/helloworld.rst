
Hello World!
============

There is how to server simple string using `yhttp`.


Install ``yhttp`` if you are not installed it yet. it's highly recommended to 
use virtual environemnt before that.

.. code-block:: bash

   pip3 install yhttp


Create a file name: ``hello.py``:

.. testcode:: 

   from yhttp import Application

   app = Application()

   @app.route()
   def get(req):
       return b'Hello World!'

   app.ready()


Serve it by your favorite ``WSGI`` server, for example:

.. code-block:: bash

   gunicorn hello:app


``yhttp`` has builtin command line interface with auto completion support. to use 
it, just call :meth:`.Application.climain` as the entry point. We will learn 
how it works in the rest of this tutorial.

Let's edit our module to act as both command line interface and WSGI
application:


.. code-block::

   import os
   import sys

   ...

   if __name__ == '__main__':
       sys.exit(app.climain())
   elif 'SERVER_SOFTWARE' in os.environ:  # Imported by a WSGI server.
       app.ready()


Now, you can run:

.. code-block:: bash

   python3 hello.py --help



   

.. testcode:: 
   :hide:

   from bddrest import Given, status, response

   with Given(app):
       assert status == 200
       assert response.text == 'Hello World!'

