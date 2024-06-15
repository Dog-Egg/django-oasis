只读与只写
==========

我们用同一个 Model 来声明请求的输入和输出。

.. oasis-literalinclude:: readonly_and_writeonly views.py

可以看到，由于字段 ``a`` 声明为“只读”。这意味着它可以作为响应的一部分发送，但不应作为请求的一部分发送；

而字段 ``b`` 声明为“只写”。因此，它可以作为请求的一部分发送，但不应作为响应的一部分发送。

.. oasis-swaggerui:: readonly_and_writeonly
    :doc-expansion: full
