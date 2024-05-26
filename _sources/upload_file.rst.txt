上传文件
========

上传文件需要用到 `django_oasis.parameter.FormData` 表单，并使用 `django_oasis.schema.File` 来声明文件字段。

.. note::
    文件上传需要使用表单，而不能使用 JSON。与普通的表单提交不同，普通表单提交时 content-type 为 application/x-www-form-urlencoded，但是上传文件需要使用 multipart/form-data。不必手动填写 content-type，``FormData`` 会自动判断使用哪种表单类型。

单文件上传
----------

.. oasis-literalinclude:: upload_file single_file.py
    :emphasize-lines: 12
    :lines: 1-16

接收到的 ``data['file']`` 值为一个 `InMemoryUploadedFile <https://docs.djangoproject.com/zh-hans/5.0/ref/files/uploads/#django.core.files.uploadedfile.InMemoryUploadedFile>`_ 对象。

多文件上传
----------

可以使用 `django_oasis.schema.List` 来声明一个文件列表。

.. oasis-literalinclude:: upload_file multiple_files.py
    :lines: 1-19

.. oasis-swaggerui:: upload_file
