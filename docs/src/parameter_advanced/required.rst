必需参数
--------

请求参数默认都是必需的，可以通过将 ``required`` 设置为 `False`，或者提供一个默认值来取消参数的必需条件。

.. oasis-literalinclude:: parameter_required schemas.py
.. oasis-literalinclude:: parameter_required views.py
.. oasis-swaggerui:: parameter_required
    :doc-expansion: full

二次改写
~~~~~~~~

`django_oasis.schema.Model` 支持通过 ``required_fields`` 参数改写其必需字段。

指定部分字段为必需字段
^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_required views_partial_required.py
    :emphasize-lines: 12

.. oasis-swaggerui:: parameter_required
    :django-settings-module: settings_partial_required.py
    :doc-expansion: full


指定所有字段为必需字段
^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_required views_all_required.py
    :emphasize-lines: 12

.. oasis-swaggerui:: parameter_required
    :django-settings-module: settings_all_required.py
    :doc-expansion: full

指定所有字段为非必需字段
^^^^^^^^^^^^^^^^^^^^^^^^

.. oasis-literalinclude:: parameter_required views_all_unrequired.py
    :emphasize-lines: 12

.. oasis-swaggerui:: parameter_required
    :django-settings-module: settings_all_unrequired.py
    :doc-expansion: full