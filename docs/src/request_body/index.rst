请求体
======


.. autoclass:: django_oasis.parameter.FormData

代码示例：

.. literalinclude:: ./formdata.py
    :lines: 1-16
    :emphasize-lines: 9-14

当 POST 表单为 ``a=1&b=1`` 时，form 值等于 ``{'a': '1', 'b': 1}``。

.. openapiview:: ./formdata.py
    :docexpansion: full

.. autoclass:: django_oasis.parameter.Body

代码示例：

.. literalinclude:: ./body.py
    :emphasize-lines: 12

.. openapiview:: ./body.py
    :docexpansion: full
