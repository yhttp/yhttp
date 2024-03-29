API Reference
=============

.. module:: yhttp
.. currentmodule:: yhttp


Base Application Class
^^^^^^^^^^^^^^^^^^^^^^ 

.. autoclass:: BaseApplication

   .. autoattribute:: settings
   .. automethod:: when
   .. automethod:: hook
   .. automethod:: ready
   .. automethod:: shutdown
   .. automethod:: climain

Application Class
^^^^^^^^^^^^^^^^^ 

.. autoclass:: Application
   :show-inheritance:

   .. automethod:: route
   .. automethod:: staticfile
   .. automethod:: staticdirectory
   .. automethod:: __call__

Rewrite Class
^^^^^^^^^^^^^ 

.. autoclass:: Rewrite
   :show-inheritance:

   .. automethod:: route
   .. automethod:: __call__

Request Class
^^^^^^^^^^^^^ 

.. autoclass:: Request

   .. autoproperty:: verb
   .. autoproperty:: path
   .. autoproperty:: fullpath
   .. autoproperty:: contentlength
   .. autoproperty:: contenttype
   .. autoproperty:: query
   .. autoproperty:: form
   .. autoproperty:: cookies
   .. autoproperty:: scheme
   .. autoproperty:: headers
   .. autoproperty:: response
   .. autoproperty:: environ


HeadersMask Class
^^^^^^^^^^^^^^^^^

.. autoclass:: HeadersMask


Response Class
^^^^^^^^^^^^^^ 

.. autoclass:: Response

   .. autoattribute:: status
   .. autoattribute:: charset
   .. autoattribute:: length
   .. autoattribute:: type
   .. autoattribute:: contenttype
   .. autoattribute:: headers

   .. automethod:: conclude
   .. automethod:: startstream
   .. automethod:: start


HeaderSet Class
^^^^^^^^^^^^^^^

.. autoclass:: HeaderSet


HTTPStatus Class
^^^^^^^^^^^^^^^^

.. autoclass:: HTTPStatus


contenttype decorators
^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: contenttype
.. autofunction:: binary
.. autofunction:: json
.. autofunction:: text
.. autofunction:: html


validate decorator
^^^^^^^^^^^^^^^^^^

.. autofunction:: validate


statuses Module
^^^^^^^^^^^^^^^

.. automodule:: yhttp.statuses
   
   .. autofunction:: status(code, text)
   .. autofunction:: badrequest()
   .. autofunction:: unauthorized()
   .. autofunction:: forbidden()
   .. autofunction:: notfound()
   .. autofunction:: methodnotallowed()
   .. autofunction:: conflict()
   .. autofunction:: gone()
   .. autofunction:: preconditionfailed()
   .. autofunction:: notmodified()
   .. autofunction:: internalservererror()
   .. autofunction:: badgateway()
   .. autofunction:: movedpermanently(url)
   .. autofunction:: found(url)
   .. autofunction:: statuscode


