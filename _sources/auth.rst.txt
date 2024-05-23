用户认证
========

仅需在 `Operation <django_oasis.core.Operation>` 上设置 auth 参数即可实现认证。

以下示例代码定义了两个接口，GET 仅需要用户登录，POST 则需要用户具有管理员权限。若用户未登录，将返回 HTTP 401 响应；若用户非管理员，将返回 HTTP 403 响应。

.. oasis-literalinclude:: auth_ views.py
    :emphasize-lines: 7, 10

.. oasis-swaggerui:: auth_


.. _custom_auth:

自定义认证
----------

继承 `django_oasis.auth.BaseAuth` 抽象类，并实现其抽象方法。


示例1
^^^^^

假设项目使用了 django.contrib.auth 作为用户认证系统，并且改用 HTTP Basic 作为认证方式。你需要自行实现认证类：

.. oasis-literalinclude:: auth_custom views.py
.. oasis-swaggerui:: auth_custom
