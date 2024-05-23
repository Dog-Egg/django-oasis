API 参考
========

Core
----

.. automodule:: django_oasis.core
    :members:


Parameter
---------

.. automodule:: django_oasis.parameter
    :members:
    :imported-members:


Pagination
----------

.. automodule:: django_oasis.pagination
    :members:
    :show-inheritance:
    :exclude-members: Pagination

.. autoclass:: django_oasis.pagination.Pagination
    :members:
    :private-members:


Auth
----

.. autoclass:: django_oasis.auth.BaseAuth
    :members:

.. note::
    以下认证类是建立在使用 django.contrib.auth 包作为项目的用户验证系统。如果你的项目使用了自定义的用户验证，请查看 :ref:`custom_auth`。

.. autoclass:: django_oasis.auth.IsAuthenticated
.. autoclass:: django_oasis.auth.IsAdministrator
.. autoclass:: django_oasis.auth.IsSuperuser
.. autoclass:: django_oasis.auth.HasPermission

Schema
------

.. automodule:: django_oasis.schema
    :members:
    :imported-members:

.. |AsField| replace:: **\*仅作为字段时有效\***
