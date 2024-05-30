路径参数 (Path)
===============

Oasis 使用 `路径模版 <https://spec.openapis.org/oas/v3.0.3#path-templating>`_ 来获取路径参数。即使用由大括号 ({}) 分隔的模板表达式，将 URL 路径的一部分标记为可使用路径参数进行替换。

路径参数会以同名关键字参数的形式传递给 API 类的 ``__init__`` 方法，如下例：


.. oasis-literalinclude:: parameter_path1 views.py

这里在 URL 路径上标记了一个名为 ``pet_id`` 的路径参数，在处理请求时，API 类也将接收到同名的关键字参数。

.. oasis-swaggerui:: parameter_path1


参数类型
--------

路径参数默认类型为 `django_oasis.schema.String`，要为路径参数设置其他类型及验证规则需使用 `Resource <django_oasis.core.Resource>` ``param_schemas`` 参数进行设置。

.. oasis-literalinclude:: parameter_path2 views.py
    :emphasize-lines: 7
.. oasis-swaggerui:: parameter_path2


Path 类型
~~~~~~~~~~

在获取路径参数时，默认是不匹配 **'/'** 的。

而 `django_oasis.schema.Path` 用于匹配非空字段，包括路径分隔符 **'/'**。它允许匹配完整的 URL 路径而不是只匹配 URL 的一部分。

如下例，当请求路径为 ``/files/image/picture.png`` 时，获取的路径参数 ``filepath`` 为 ``image/picture.png``。

.. oasis-literalinclude:: parameter_path3 views.py


参数样式查询表
--------------

路径参数同样支持参数样式，使用 ``param_styles`` 参数进行设置。

数组样式
~~~~~~~~~

blue,black,brown (default)
^^^^^^^^^^^^^^^^^^^^^^^^^^

以下示例的参数结果示例 ``color = ["blue", "black", "brown"]``

.. oasis-literalinclude:: parameter_path_styles views.py
   :lines: 6-20

对象样式
~~~~~~~~~

以下示例的参数结果示例 ``color = {"R": 100, "G": 200, "B": 500}``

R,100,G,200,B,150 (default)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_path_styles views.py
    :lines: 24-44

R=100,G=200,B=150
^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_path_styles views.py
    :lines: 48-68

.. oasis-swaggerui:: parameter_path_styles
