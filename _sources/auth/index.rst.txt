用户认证
========

仅需使用 `Operation <django_oasis.Operation>` 并设置 auth 参数即可实现认证。

以下代码示例会验证请求是否具有“管理员权限”。若用户未登录，将返回 HTTP 401 响应；若用户已登录但非管理员，将返回 HTTP 403 响应。

.. myliteralinclude:: ./auth.py
    :emphasize-lines: 7

.. openapiview:: ./auth.py


内置认证类
----------

.. note::

    以下认证类是建立在使用 django.contrib.auth 包作为项目的用户验证系统。如果你的项目使用了自定义的用户验证，请查看 :ref:`custom_auth`。

.. automodule:: django_oasis.auth
    :members: IsAdministrator, IsAuthenticated, IsSuperuser, HasPermission


.. _custom_auth:

自定义认证
----------

.. autoclass:: django_oasis.auth.BaseAuth
    :members:
    :special-members: __openapispec__

示例1
^^^^^

假设项目使用了 django.contrib.auth 作为用户认证系统，并且改用 HTTP Basic 作为认证方式。你需要自行实现认证类：

.. myliteralinclude:: ./custom_auth.py
.. openapiview:: ./custom_auth.py
