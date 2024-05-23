分页
====

Oasis 提供了对 Django QuerySet 对象进行分页的方法，仅需 2 行代码即可实现数据分页。


内置分页器
----------

下面的示例将对 ``Book`` 模型实现 2 种分页查询方式。

.. oasis-literalinclude:: pagination models.py


`PagePagination <django_oasis.pagination.PagePagination>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: pagination page_pagination.py
    :emphasize-lines: 14,16


`OffsetPagination <django_oasis.pagination.OffsetPagination>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: pagination offset_pagination.py
    :emphasize-lines: 14,16

.. warning::
    使用分页器时，无需为 Operation 设置 response_schema 参数，分页器在设置时会自动为其填充。

.. oasis-swaggerui:: pagination


自定义分页器
------------

分页器是高度可定制的，只需继承 `django_oasis.pagination.Pagination` 抽象类，并实现其抽象方法。

.. oasis-literalinclude:: pagination_custom views.py
.. oasis-swaggerui:: pagination_custom
    :doc-expansion: full
