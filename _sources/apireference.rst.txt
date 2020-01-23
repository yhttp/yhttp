API Reference
=============

.. module:: yhttp
.. currentmodule:: yhttp

Application Class
^^^^^^^^^^^^^^^^^ 

.. autoclass:: Application

   .. automethod:: route
   .. automethod:: climain
   .. automethod:: staticfile
   .. automethod:: staticdirectory
   .. automethod:: when
   .. automethod:: hook
   .. automethod:: staticfile
   .. automethod:: staticdirectory
   .. automethod:: ready
   .. automethod:: shutdown
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

   .. automethod:: conclude
   .. automethod:: startstream
   .. automethod:: start


HTTPStatus Class
^^^^^^^^^^^^^^^^

.. autoclass:: HTTPStatus


contenttype decorators
^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: contenttype
.. autofunction:: binary
.. autofunction:: json
.. autofunction:: text



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

