.. yhttp documentation master file, created by
   sphinx-quickstart on Tue Jan 21 16:31:18 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to yhttp's documentation!
=================================

A lightweight flask-like HTTP framework.

Python >= 3.6

.. code-block:: bash

   pip install yhttp


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


Features
********

- Very simple, less-code & fast.
- Regex route.
- Url-Encoded, Multipart and JSON form parsing.
- A very flexible configuration system: 
  `pymlconf <https://github.com/pylover/pymlconf>`_
- Use Python's `keywordonly <https://www.python.org/dev/peps/pep-3102/>`_ 
  arguments for query strings (>= 0.24.0).
- Easy to extend.
- Builtin extensible CLI.


Contents
********

.. toctree::
   :maxdepth: 3

   quickstart
   cookbook
   tutorials/index
   apireference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
