请求头参数 (Header)
===================

声明和获取请求头参数可直接参考 :doc:`parameter_query` 章节。他们的实现方式是一样的（参数样式有差异），仅仅是获取参数的位置不同，所以使用以下类同理替换即可。

- `django_oasis.parameter.Header`
- `django_oasis.parameter.HeaderItem`


参数样式查询表
--------------

数组样式
~~~~~~~~

以下示例的参数结果示例 ``color = ["blue", "black", "brown"]``

color: blue,black,brown (default)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_header_styles views.py
    :lines: 6-15

.. oasis-swaggerui:: parameter_header_styles

