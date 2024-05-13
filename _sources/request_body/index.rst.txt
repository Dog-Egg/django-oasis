请求体
======

JSON 格式
---------

代码示例：

.. myliteralinclude:: jsondata.py
    :lines: 1-16
    :emphasize-lines: 9-14
.. openapiview:: jsondata.py
    :docexpansion: full


表单格式
--------

代码示例：

.. myliteralinclude:: ./formdata.py
    :lines: 1-16
    :emphasize-lines: 9-14

当 POST 表单为 ``a=1&b=1`` 时，form 值等于 ``{'a': '1', 'b': 1}``。

.. openapiview:: ./formdata.py
    :docexpansion: full


Body
----

代码示例：

.. myliteralinclude:: ./body.py
    :emphasize-lines: 12

.. openapiview:: ./body.py
    :docexpansion: full
