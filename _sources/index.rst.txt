.. yhttp documentation master file, created by
   sphinx-quickstart on Tue Jan 21 16:31:18 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to yhttp's documentation!
=================================

.. image:: http://img.shields.io/pypi/v/yhttp.svg
     :target: https://pypi.python.org/pypi/yhttp
 
.. image:: https://travis-ci.org/yhttp/yhttp.svg?branch=master
   :target: https://travis-ci.org/yhttp/yhttp

.. image:: https://coveralls.io/repos/github/yhttp/yhttp/badge.svg?branch=master
   :target: https://coveralls.io/github/yhttp/yhttp?branch=master

.. image:: https://img.shields.io/badge/Python-%3E%3D3.6-blue
   :target: https://python.org


A lightweight flask-like HTTP framework.

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
- Regex :ref:`route <cookbook-routing>`.
- UrlEncoded, Multipart and JSON :ref:`form parsing <cookbook-form>`.
- A very flexible :ref:`configuration <cookbook-settings>` system.
- Use Python's `keywordonly <https://www.python.org/dev/peps/pep-3102/>`_ 
  arguments for query strings.
- Easy to extend.
- Builtin extensible CLI.
- Request :ref:`Validation <cookbook-validation>`

Contents
********

.. toctree::
   :maxdepth: 2

   tutorials/index
   cookbook
   apireference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
