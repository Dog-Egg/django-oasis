请求响应
========

Oasis 的请求操作可以如视图函数一样返回请求响应 (`HttpResponseBase <https://docs.djangoproject.com/zh-hans/5.0/ref/request-response/#httpresponsebase-class>`_ 对象)。

但为了开发便利，请求操作也可以不必直接返回请求响应。

返回字符串
-----------

.. literalinclude:: ../samples/response/views_str.py
    :lines: 6-9

.. note:: 等同于

    .. literalinclude:: ../samples/response/views_str.py
        :lines: 12-15


返回可被 JSON 编码的对象
-------------------------

.. literalinclude:: ../samples/response/views_dict.py
    :lines: 6-9

.. note:: 等同于

    .. literalinclude:: ../samples/response/views_dict.py
        :lines: 12-15

返回 `None`
------------

.. literalinclude:: ../samples/response/views_none.py
    :lines: 6-9

.. note:: 等同于

    .. literalinclude:: ../samples/response/views_none.py
        :lines: 12-15


Response Schema
---------------

当返回一个不可被正常编码的对象时，可以通过使用 ``response_schema`` 参数设置一个 `Schema <django_oasis.schema.Schema>`，它会在响应过程中对返回值进行序列化。

.. oasis-literalinclude:: response response_schema.py
    :emphasize-lines: 23

.. note:: 等同于

    .. literalinclude:: ../samples/response/response_schema2.py
        :lines: 10-18

    虽然结果一致，但是 response_schema 还会为 OAS 提供响应描述。

.. oasis-swaggerui:: response
