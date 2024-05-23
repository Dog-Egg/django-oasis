请求操作
========

下例定义了所有可被识别的请求操作。

.. oasis-literalinclude:: operations views.py

.. oasis-swaggerui:: operations


Request 对象
-------------

在使用 Oasis 开发时，很多时候都不需要直接使用到 Request 对象，所以请求操作并不像 Django 视图函数一样会收到 Request 对象。

因此 Oasis 做了如下规定: 只有定义了 ``__init__`` 方法的 API 类才会收到 Request 对象，且 Request 对象会以第一个位置参数的形式传递给 ``__init__`` 方法。该 Request 对象为 Django 的 `HttpRequest <https://docs.djangoproject.com/en/4.2/ref/request-response/#httprequest-objects>`_ 对象。

.. oasis-literalinclude:: request_object views.py


Operation 装饰类
----------------

`Operation <django_oasis.core.Operation>` 赋予请求操作更丰富的能力。比如提供说明文档，定义响应结构等等。

.. oasis-literalinclude:: operation views.py

.. oasis-swaggerui:: operation