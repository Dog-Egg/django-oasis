多实例布局
==========

可以按照 Django 的应用布局，设置多个 OpenAPI 实例。

应用1

.. oasis-literalinclude:: layout_multi_instances app1/urls.py

应用2

.. oasis-literalinclude:: layout_multi_instances app2/urls.py

项目 urls.py

.. oasis-literalinclude:: layout_multi_instances urls.py

.. oasis-swaggerui:: layout_multi_instances