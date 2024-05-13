路径参数
========

Oasis 使用 `路径模版 <https://spec.openapis.org/oas/v3.0.3#path-templating>`_ 来获取路径参数。即使用由大括号 ({}) 分隔的模板表达式，将 URL 路径的一部分标记为可使用路径参数进行替换。

路径参数会以同名关键字参数的形式传递给 API 类的 ``__init__`` 方法，如下例：

.. myliteralinclude:: ./example.py

这里在 URL 路径上标记了一个名为 ``pet_id`` 的路径参数，在处理请求时，API 类也将接收到同名的关键字参数。

.. openapiview:: ./example.py
    :docExpansion: full


参数类型
--------

为路径参数声明数据类型及验证规则只需为 `Resource <django_oasis.core.Resource>` 设置 ``param_schemas``。

.. myliteralinclude:: ./example2.py
    :emphasize-lines: 6

Schema 对象会对对应的路径参数执行反序列化；如果反序列化失败，会返回 HTTP 404 响应。

.. openapiview:: ./example2.py
    :docExpansion: full


Path 类型
---------

在获取路径参数时，默认是不匹配 **'/'** 的。

而 `schema.Path <django_oasis.schema.Path>` 用于匹配非空字段，包括路径分隔符 **'/'**。它允许你匹配完整的 URL 路径而不是只匹配 URL 的一部分。

如下例，当请求路径为 ``/files/image/picture.png`` 时，获取的路径参数 ``filepath`` 为 ``image/picture.png``。

.. myliteralinclude:: ./example3.py


参数样式
--------

路径参数同样支持参数样式，通过 ``param_styles`` 进行设置。参数样式遵照 OpenAPI 规范的定义，请参照 `样式值 <https://spec.openapis.org/oas/v3.0.3#style-values>`_ 和 `样式示例 <https://spec.openapis.org/oas/v3.0.3#style-examples>`_ 进行设置。

.. myliteralinclude:: ./example4.py
    :emphasize-lines: 10

此示例请求路径如果为 ``/color/blue,red``，则获取的 ``colors`` 值为 ``['blue', 'red']``。

.. openapiview:: ./example4.py
    :docExpansion: full
