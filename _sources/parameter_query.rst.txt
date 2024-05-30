查询参数 (Query)
================

声明和获取查询参数需要使用 `django_oasis.parameter.Query`，它的使用方法如下:

.. oasis-literalinclude:: parameter_query1 views.py
    :emphasize-lines: 8-10, 17

如示例所见，查询参数的声明由2部分组成:

* ``QuerySchema`` 是一个 Schema 类，它用于定义请求参数名、数据类型等，并且为实际的请求参数执行反序列化及验证。有关 Schema 的详细说明请查看 :doc:`相应章节 <../schema/index>`。
* `Query <django_oasis.parameter.Query>` 用于声明请求参数位于 "查询参数" 中。

最终 ``get`` 方法获取的 ``query`` 参数值为 ``QuerySchema`` 对请求参数反序列化后得到的值。

在此示例中，如果查询参数为 ``?a=1&b=2``，则 ``query = {"a": "1", "b": 2}``。

.. oasis-swaggerui:: parameter_query1
    :doc-expansion: full


简洁写法
--------

在声明请求参数时，可以使用字典代替 Schema，这样写起来更加简洁。如下代码等同于上面的示例。

.. code-block::
    :emphasize-lines: 5-8

    @Resource("/to/path")
    class API:
        def get(
            self,
            query=Query({
                'a': schema.String(),
                'b': schema.Integer()
            }),
        ): ...

.. note::
    实际上，在使用字典代替 Schema 时，``Query`` 内部调用了 `Model.from_dict <django_oasis.schema.Model.from_dict>` 方法。


分组声明
--------

请求参数支持分组声明，这可以实现对参数的分组获取。

.. oasis-literalinclude:: parameter_query2 views.py
    :emphasize-lines: 10-11

``q1`` 和 ``q2`` 将查询参数拆分为了两组。

如查询参数为 ``?a=1&b=2&c=3``，则 ``q1 = {"a": "1", "b": "2"}`` ``q2 = {"c": "3"}``。

.. oasis-swaggerui:: parameter_query2
    :doc-expansion: full


声明单个参数
------------

如果仅需要对单个参数项进行声明，使用 `django_oasis.parameter.QueryItem` 。

.. oasis-literalinclude:: parameter_query3 views.py

.. note::
    ``QueryItem`` 本身并不参与实际功能，它只是被转换为了 ``Query`` 的形式。所以上面代码等效于：

    .. code-block::

        @Resource("/to/path")
        class API:
            def get(self, query=Query({
                "a": schema.Integer(),
                "b": schema.Integer(default=0),
            })): ...


参数样式查询表
--------------

数组样式
~~~~~~~~

以下示例的参数结果示例 ``color = ["blue", "black", "brown"]``

color=blue&color=black&color=brown (default)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_query_styles views.py
    :lines: 6-15

color=blue,black,brown
^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_query_styles views.py
    :lines: 19-28

color=blue black brown
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_query_styles views.py
    :lines: 32-41

color=blue|black|brown
^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_query_styles views.py
    :lines: 45-54


对象样式
~~~~~~~~

以下示例的参数结果示例 ``color = {"R": 100, "G": 200, "B": 500}``

R=100&G=200&B=150 (default)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_query_styles views.py
    :lines: 58-73

color=R,100,G,200,B,150
^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_query_styles views.py
    :lines: 77-92

color[R]=100&color[G]=200&color[B]=150
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_query_styles views.py
    :lines: 96-111

.. oasis-swaggerui:: parameter_query_styles