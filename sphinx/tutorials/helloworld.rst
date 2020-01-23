Hello World!
============

There is how to server simple string using `yhttp`.


Install ``yhttp`` if you are not installed it yet. it's highly recommended to 
use virtual environment before that. I use
`virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/en/latest/>`_.

Create a virtual environment to isolate your hello world application from the 
rest of the system python packages.

.. code-block:: bash

   mkvirtualenv hello


.. code-block:: bash

   workon hello
   pip3 install yhttp


Create a file named: ``hello.py``:

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


Serve it by your favorite ``WSGI`` server, for example:

.. code-block:: bash

   pip install gunicorn
   gunicorn hello:app


Use your favorite http clinet to check it:

.. code-block:: bash

   curl localhost:8000


======================
Command Line Interface
======================

``yhttp`` has builtin command line interface with auto completion support. 
to use it, just call :meth:`.Application.climain` as the entry point. We will 
learn how it works in the rest of this tutorial.

Let's edit ``hello.py`` to act as both command line interface and WSGI
application:


.. code-block::

   import sys

   ...

   if __name__ == '__main__':
       sys.exit(app.climain())
    
   app.ready()


Now, you can run:

.. code-block:: bash

   python3 hello.py --help

You can set the execution bit of the ``hello.py`` and add a shebang at the
first line to use it as a standalone executable.

.. code-block:: bash

   chmod +x hello.py


And insert it at the first line:

.. code-block:: bash

   #! /usr/bin/env python3


Lets take a look at ``hello.py``.

.. code-block::

   #! /usr/bin/env python3
   
   import sys
   
   from yhttp import Application
   
   
   app = Application()
   
   
   @app.route()
   def get(req):
       return b'Hello World!'
   
   
   if __name__ == '__main__':
       sys.exit(app.climain())
   
   
   app.ready()


Use it as an executable python script:

.. code-block:: bash

   ./hello.py --help


There is also a subcommand ``serve`` to serve the WSGI application by python's
builtin WSGI server.


.. code-block:: bash

   ./hello.py serve


Use ``--help`` anywhere to know command line options:

.. code-block:: bash

   ./hello.py serve --help


.. code-block:: bash

   usage: hello.py serve [-h] [-b {HOST:}PORT] [-C DIRECTORY]

   optional arguments:
     -h, --help            show this help message and exit
     -b {HOST:}PORT, --bind {HOST:}PORT
                           Bind Address. default: 8080
     -C DIRECTORY, --directory DIRECTORY
                           Change to this path before starting, default is: `.`


==============
Python Package
==============

Create a ``setup.py``.

.. code-block::

   from setuptools import setup
   
   
   setup(
       name='hello',
       version='0.1.0',
       install_requires=[
           'yhttp',
       ],
       py_modules=['hello'],
       entry_points={
           'console_scripts': [
               'hello = hello:app.climain'
           ]
       },
   )


After this, you can install the module as a reqular python package.

.. code-block:: bash

   workon hello
   pip install -e .


So, use the ``hello`` command without specifying path and extension, thanks to 
setuptools ``entry_points`` feature.

.. code-block:: bash

   hello --help

   hello serve --bind 8088


===================
Bash Autocompletion
===================

Just run:

.. code-block:: bash

   ./hello.py completion install

Then deactivate and re-activate your virtual environment to apply changes:

.. code-block:: bash

   deactivate && workon hello


Write ``hello`` and hit the ``TAB`` key twice to see the avaiable options:

.. code-block:: bash

   hello TAB TAB

Check out the other tutorials to discover the ``yhttp`` features.
