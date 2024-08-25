API Reference
=============

.. module:: yhttp.core
.. currentmodule:: yhttp.core


Application Classes
^^^^^^^^^^^^^^^^^^^ 

.. autoclass:: BaseApplication


.. autoclass:: Application
   :show-inheritance:


Rewrite Class
^^^^^^^^^^^^^ 

.. autoclass:: Rewrite
   :show-inheritance:

Request Class
^^^^^^^^^^^^^ 

.. autoclass:: Request


HeadersMask Class
^^^^^^^^^^^^^^^^^

.. autoclass:: HeadersMask


Response Class
^^^^^^^^^^^^^^ 

.. autoclass:: Response


HeaderSet Class
^^^^^^^^^^^^^^^

.. autoclass:: HeaderSet


MultiDict
^^^^^^^^^

.. autoclass:: MultiDict


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


gurad Module
^^^^^^^^^^^^

.. automodule:: yhttp.core.guard
   :special-members: __call__


validation module
^^^^^^^^^^^^^^^^^
.. currentmodule:: yhttp.core

.. deprecated:: 5.1
   Use :mod:`.guard` instead.

.. autofunction:: validate_form
.. autofunction:: validate_query


statuses Module
^^^^^^^^^^^^^^^

.. currentmodule:: yhttp.core.statuses

.. automodule:: yhttp.core.statuses
