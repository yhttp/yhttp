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

   .. autoproperty:: query
   .. autoproperty:: form
   .. autoproperty:: cookies


Response Class
^^^^^^^^^^^^^^ 

.. autoclass:: Response

   .. autoattribute:: status

 
HTTPStatus Class
^^^^^^^^^^^^^^^^

.. autoclass:: HTTPStatus


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


.. 
  Field class

