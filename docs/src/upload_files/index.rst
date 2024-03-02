上传文件
========

上传文件需要用到 `FormData <django_oasis.parameter.FormData>` 或者 `FormItem <django_oasis.parameter.FormItem>`，并使用 `File <django_oasis.schema.File>` 来声明文件类型。

.. note::
    文件上传需要使用表单，而不能使用 JSON。与普通的表单提交不同，普通表单提交时 content-type 为 application/x-www-form-urlencoded，但是上传文件需要使用 multipart/form-data。这只是顺便一说，了解就行，Oasis 会自动判断使用哪种表单类型。

示例代码：

.. myliteralinclude:: ./uploadfile.py
    :lines: 1-11
    :emphasize-lines: 9

接收到的 file 值为一个 `InMemoryUploadedFile <https://docs.djangoproject.com/zh-hans/5.0/ref/files/uploads/#django.core.files.uploadedfile.InMemoryUploadedFile>`_ 对象。

.. openapiview:: ./uploadfile.py
    :docexpansion: full