快速入门
========

安装
----

由于 Oasis 处于开发阶段，并未发布在 pypi 上，所以仅提供从 Github 安装。(建议在虚拟环境中安装，如 `virtualenv <https://virtualenv.pypa.io>`_)

.. code-block:: bash

    $ pip install git+https://github.com/Dog-Egg/django-oasis.git


使用
----

Oasis 是作为 Django 路由的一部分运行的，所以它可以很轻松地在已有的 Django 项目中被添加。如果还有没有项目，可以查看 `官方文档 <https://docs.djangoproject.com/zh-hans/4.2/intro/tutorial01/#creating-a-project>`_ 进行创建。


设置应用
^^^^^^^^

将 ``django_oasis`` 添加到 ``INSTALLED_APPS`` 列表中。

.. code-block::
    :emphasize-lines: 4

    INSTALLED_APPS = [
        "django.contrib.admin",
        ...
        "django_oasis",
    ]

.. note::
    这一步并不是必须的，如果不需要使用 Oasis 提供的 API 文档模板，可以跳过这一步。但要完成此示例，必须设置 ``django_oasis``。


编写 API
^^^^^^^^
编写如下 API，它像 Django 的视图函数一样，负责处理请求并返回响应。 (按照 Django 的项目结构，可以将 API 代码放置在 ``views.py`` 文件中。)

.. oasis-literalinclude:: quickstart views.py

* ``GreetingAPI`` 类是一个 API 类，它是普通的 Python 类，并且不需要继承特定的父类。
* `Resource <django_oasis.core.Resource>` 提供路由端点，并将 API 类标记为请求资源。
* ``get`` 方法会被识别为一个请求操作，它是请求处理的单元。这里表示该请求资源可以处理 GET 请求。


添加路由
^^^^^^^^

最后将 API 添加到 `OpenAPI <django_oasis.core.OpenAPI>` 实例中，并将 OpenAPI 实例的路由添加到 Django 路由配置中。

.. oasis-literalinclude:: quickstart urls.py
    :emphasize-lines: 8, 9, 12


查看文档
^^^^^^^^

运行 Django 开发服务

.. code-block:: bash

    $ python manage.py runserver

并访问 http://localhost:8000/docs/，将看到如下的文档页面。

.. oasis-swaggerui:: quickstart
