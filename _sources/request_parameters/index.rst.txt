请求参数
========

实际上，按照 OpenAPI 规范定义，请求参数可以来自以下 4 个部分：

* URL 路径 (path)
* URL 参数 (query)
* 请求头 (header)
* 请求 cookie (cookie)

本篇内容仅先说明从“URL 参数”，“请求头”及“请求 cookie”中获取请求参数，因为它们在 Oasis 中的实现和使用方法相同；“URL 路径” 使用方法略有不同，所以将 :doc:`../request_path/index` 一篇中单独介绍。


参数声明
--------

Oasis 可以直接通过声明获取请求参数，并且为参数执行反序列化和验证，如下例：

.. myliteralinclude:: ./declare_params.py
    :emphasize-lines: 5-7,12

如示例所见，参数的声明由 2 个部分组成：

* ``QuerySchema`` 是一个 Schema 对象，它用于定义请求参数名、数据类型等，并且为实际的请求参数执行反序列化及验证。有关 Schema 的详细说明请查看 :doc:`相应章节 <../schema/index>`。
* `Query <django_oasis.parameter.Query>` 用于声明请求参数位于 "URL 参数" 中。

最终 ``get`` 操作获取的 ``query`` 参数值为 ``QuerySchema`` 对请求参数反序列化后得到的值。

此示例中，如果 URL 请求参数为 ``?a=1&b=2``，则 ``query = {"a": "1", "b": 2}``。

.. note::
    * `django_oasis.parameter.Cookie` 用于声明请求 cookie 中的参数；
    * `django_oasis.parameter.Header` 用于声明请求头中的参数；

    使用方法如上述代码中的 `Query <django_oasis.parameter.Query>` 对象一样。


.. openapiview:: ./declare_params.py
    :docExpansion: full


简单写法
--------

在声明请求参数时，可以使用字典代替 Schema，这看起来更加简洁。如下代码等同于上面的示例。

.. code-block::
    :emphasize-lines: 5-8

    @Resource("/to/path")
    class API:
        def get(
            self,
            query=Query({
                'a': schema.String(),
                'b': schema.Integer(default=1)
            }),
        ):
            ...

.. note::
    实际上，当使用字典代替 Schema 时，内部调用了 `Model.from_dict <django_oasis.schema.Model.from_dict>` 方法。


分组声明
--------

`Query <django_oasis.parameter.Query>`, `Cookie <django_oasis.parameter.Cookie>`, `Header <django_oasis.parameter.Header>` 支持分组声明，这可以实现对参数的分组需要。

.. myliteralinclude:: ./param_groups.py
    :emphasize-lines: 9-10

``q1`` 和 ``q2`` 即把 URL 参数拆分为了两组。

如请求参数为 ``?a=1&b=2&c=3``，则 ``q1 = {"a": "1", "b": "2"}`` ``q2 = {"c": "3"}``。

.. hint::
    :doc:`../pagination` 功能也利用了这一特性。

.. openapiview:: ./param_groups.py
    :docExpansion: full


参数样式
--------

参数样式遵照 OpenAPI 规范的定义，请参照 `样式值 <https://spec.openapis.org/oas/v3.0.3#style-values>`_ 和 `样式示例 <https://spec.openapis.org/oas/v3.0.3#style-examples>`_ 进行设置。

.. note::
    样式默认值并未完全遵守 OAS 定义 (如 cookie 位置被默认设置为了 style=form, explode=false)，你可能会发现与 OAS 定义中的不同；但是 Oasis 在生成的 OAS 内容中始终显示设置了参数样式，所以并无大碍。

下面示例将展示参数样式的设置方法。

.. myliteralinclude:: ./param_style.py
    :emphasize-lines: 14-17

此示例对应的 URL 参数如果为 ``?a=1&a=2&b=1,2``，则所得的 ``query = {'a': ['1', '2'], 'b': ['1', '2']}``。

.. openapiview:: ./param_style.py


声明单个参数
------------

上面介绍的 ``Query``, ``Cookie``, ``Header`` 都是对参数进行整体声明。

如果你需要对单个参数项进行声明，可以使用 `QueryItem <django_oasis.parameter.QueryItem>`, `CookieItem <django_oasis.parameter.CookieItem>` 和 `HeaderItem <django_oasis.parameter.HeaderItem>`。

.. myliteralinclude:: ./paramitem.py

.. note::
    像 ``QueryItem`` 本身并不参与实际功能，它只是被转换为了 ``Query`` 的形式。所以上面代码等效于：

    .. code-block::

        @Resource("/to/path")
        class API:
            def get(self, query=Query({
                "a": schema.Integer(),
                "b": schema.Integer(default=0),
            })):
                ...

.. openapiview:: ./paramitem.py
    :docExpansion: full
