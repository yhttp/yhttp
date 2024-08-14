Test Driven Url Shortener
=========================

In this tutorial we'll develop a simple URL shorotener using ``redis`` 
storage and ``yhttp``.

It's highly recommended to use virtual environment before that. I use
`virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/en/latest/>`_.

Create a virtual environment to isolate your application from the rest of the 
system python packages.

.. code-block:: bash

   mkvirtualenv shortener


Rrequirements
-------------

Activate your virtual environment if you're not activated it yet.

.. code-block:: bash

   workon shortener


I use `bddrest <https://github.com/pylover/bddrest>`_ to test python ``WSGI``
applications.

Create a directory named: ``shortener``.

.. code-block:: bash

   mkdir shortener
   cd shortener

And place the file ``requirements-dev.txt`` inside it. this is a way to 
separate developement dependencies from runtime requirements.

``requirements-dev.txt``

.. code-block:: bash

   bddrest
   pytest-cov


Then install them by:

.. code-block:: bash

   pip install -r requirements-dev.txt


Project Structure
-----------------

.. code-block::

   shortener/
   ├── requirements-dev.txt
   ├── setup.py
   ├── shortener.py
   ├── tests.py
   └── wsgi.py


setup.py
--------

Create a file named ``setup.py`` to use our project as a reqular python
package.

``setup.py``

.. code-block::


   from setuptools import setup
   
   
   dependencies = [
       'yhttp >= 2.5, < 3',
       'redis',
   ]
   
   
   setup(
       name='shortener',
       version='0.1',
       description='Url shortener web application',
       install_requires=dependencies,
       py_modules=['shortener'],
       entry_points=dict(console_scripts='shortener=shortener:app.climain'),
       license='MIT',
   )


Install the project with pip's `-e/--editable` flag:

.. code-block:: bash

   pip install -e .


Behavioral Test
---------------

Let's write some tests to clear what we need. create a file named ``tests.py``
inside the ``shortener`` directory.

``tests.py``

.. code-block::

   import os
   import random
   import string
   
   import pytest
   from bddrest import Given, status, when, response, given
   
   from shortener import app
   
   
   @pytest.fixture
   def randommock():
       backup = random.randint
       random.randint = lambda a, b: 0xF00
       yield
       random.randint = backup
   
   
   @pytest.fixture
   def redismock():
       import shortener
   
       class RedisMock:
           def __init__(self):
               self.maindict = dict()
   
           def get(self, key):
               return self.maindict.get(key, '').encode()
   
           def set(self, key, value):
               self.maindict[key] = value
   
       backup = shortener.redis
       shortener.redis = RedisMock()
       yield shortener.redis
       shortener.redis = backup
   
   
   def test_shortener(randommock, redismock):
       with Given(
           app,
           verb='POST',
           json=dict(url='http://example.com')
       ):
           assert status == 201
           assert response.text == 'f00'
   
           when(json=dict(url='invalidurl'))
           assert status == 400
   
           when(json=given - 'url')
           assert status == '400 Field missing: url'


Implement Shortener API
-----------------------

``shortener.py``

.. code-block::

   import random
   
   import redis
   from yhttp import Application, text, statuses, validate_form, statuscode
   
   
   app = Application()
   redis = redis.Redis()
   
   
   def store(url):
       freshid = hex(random.randint(0x0001, 0xFFFF))[2:]
       redis.set(freshid, url)
       return freshid
   
   
   @app.route()
   @validate_form(fields=dict(
       url=dict(
           required='400 Field missing: url',
           pattern=(r'^http://.*', '400 Invalid URL')
       )
   ))
   @text
   @statuscode('201 Created')
   def post(req):
       return store(req.form['url'])


Test your API:

.. code-block:: bash

   pytest --cov=shortener tests.py


Redirector API
--------------

Append this test case to ``tests.py``:


.. code-block::

   def test_redirector(redismock):
       redismock.set('foo', 'https://example.com')
       with Given(
           app,
           url='/foo'
       ):
           assert status == 302
           assert response.headers['LOCATION'] == 'https://example.com'
   
           when(url='/notexists')
           assert status == 404


And add this handler to the ``shortener.py``:

.. code-block::

   @app.route('/(.*)')
   def get(req, key):
       longurl = redis.get(key)
       if not longurl:
           raise statuses.notfound()
   
       raise statuses.found(longurl.decode())


Test redirector API:

.. code-block:: bash

   pytest --cov=shortener tests.py


Seems everything is fine. run the development server and use ``curl`` to play
with your api:

.. code-block:: bash

   shortener s -b 8000

Open another terminal and try to shor a url:

.. code-block:: bash

   curl localhost:8000 -XPOST -F'url=http://example.com'

It will returns something like this:

.. code-block:: bash

   bf2


Use the ``POST`` response to get the original URL:

.. code-block:: bash

   curl -i localhost:8000/bf2

.. code-block::

   HTTP/1.0 302 Found
   Date: Tue, 28 Jan 2020 18:36:04 GMT
   Server: WSGIServer/0.2 CPython/3.6.9
   location: http://example.com
   content-type: text/plain; charset=utf-8
   content-length: 9
   
   302 Found

Or redirect to the original url:

.. code-block:: bash

   curl -L localhost:8000/bf2

That's it. your url shortener is ready to use with the other ``WSGI`` servers
using this script:

``wsgi.py``

.. code-block::

   from shortener import app

   
   app.ready()

Then use your favorite wsgi server to serve it:

.. code-block:: bash

   pip install gunicorn
   gunicorn wsgi:app

Checkout the 
`complete project <https://github.com/yhttp/urlshortener-example>`_ on github, 
other :ref:`tutorials` and or :ref:`cookbook` to discover more 
features.

