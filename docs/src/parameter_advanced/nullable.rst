可为 null 的参数
================

默认条件下，参数均不可为 ``null`` (Python 中叫 `None`)。可设置 ``nullable=True`` 允许参数为 ``null``。

.. oasis-literalinclude:: parameter_nullable views.py
    :emphasize-lines: 13

.. oasis-swaggerui:: parameter_nullable
    :doc-expansion: full