擦除无意义的参数
=================

这是 `django_oasis.schema.Model` 的功能，但是对于查询参数来说可能非常有用。

客户端在请求时经常会发送像这样的查询参数：``?a=&b=1``。在这个请求中，客户端发送的参数 ``a`` 是一个空字符串，但并不表示服务端应该接收这样的空字符串，服务端更希望不要传递这样的参数。

所以 `django_oasis.schema.Model` 提供了 “擦除”(erase) 字段的功能。默认将空字符串或仅包含空白字符的字符串擦除。

.. oasis-literalinclude:: parameter_erase views.py
    :lines: 1-17

当查询参数如 ``?a=&b=1`` 时，得到的结果 ``query = {'b': '1'}``。


取消擦除
--------

如果需要接收空字符串参数，可以将 ``erase`` 设置 `None` 来取消擦除功能。

.. oasis-literalinclude:: parameter_erase_none views.py
    :lines: 1-20
    :emphasize-lines: 13

当查询参数如 ``?a=&b=1`` 时，得到的结果 ``query = {'a': '', 'b': '1'}``。