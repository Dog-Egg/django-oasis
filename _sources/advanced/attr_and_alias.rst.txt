属性名与别名
============

首先来理清几个名词概念：“字段名”，“属性名” 和 “别名”。

.. oasis-literalinclude:: attr_and_alias schemas.py

在这个示例中，``Model`` 有一个字段 ``a``。其中字面量 "a" 即为字段的字段名，它是不可变的。

而 ``attr`` 和 ``alias`` 参数则是用于设置 “属性名” 和 “别名” 的，它们分别对应了序列化和反序列化结果的字段名映射。默认情况下，它们都等于字段名。

.. testcode::
    :hide:

    from samples.attr_and_alias.schemas import Model

这是它的序列化和反序列化运行结果:

.. doctest::

    >>> Model().serialize({'attr': 1})
    {'alias': 1}

    >>> Model().deserialize({'alias': 1})
    {'attr': 1}

将其应用于请求中，则 “属性名” 对应用于服务端，而 “别名” 对应用于客户端。

.. oasis-literalinclude:: attr_and_alias views.py
.. oasis-swaggerui:: attr_and_alias
    :doc-expansion: full