请求体 (Body)
=============

JSON 格式
----------

使用 `django_oasis.parameter.JsonData` 或 `django_oasis.parameter.JsonItem` 声明。

.. oasis-literalinclude:: parameter_body_json views.py
.. oasis-swaggerui:: parameter_body_json


表单格式
--------

使用 `django_oasis.parameter.FormData` 或 `django_oasis.parameter.FormItem` 声明。

.. oasis-literalinclude:: parameter_body_form views.py
.. oasis-swaggerui:: parameter_body_form