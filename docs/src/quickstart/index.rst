开始
====

本篇内容将从安装开始，引导你创建一个简单的项目，并查看接口文档。

安装
----

需要安装 Django 和 Django-Oasis，由于 Oasis 处于开发阶段，并未发布在 pypi 上，所以仅提供从 Github 安装。(建议在虚拟环境中安装，如 `virtualenv <https://virtualenv.pypa.io>`_)

.. code-block:: bash

    $ pip install -U django
    $ pip install git+https://github.com/Dog-Egg/django-oasis.git


创建 Django 项目
----------------

cd 到一个你想放置你代码的目录，然后运行以下命令：

.. code-block:: bash

    $ django-admin startproject mysite .
    $ python manage.py startapp myapp

通过以上命令，便可得到如下的项目结构。更多关于 Django 项目创建的介绍请查看其 `官方文档 <https://docs.djangoproject.com/zh-hans/4.2/intro/tutorial01/#creating-a-project>`_ 。

.. code-block::

    .
    ├── manage.py
    ├── mysite
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── myapp
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── migrations
        │   └── __init__.py
        ├── models.py
        ├── tests.py
        └── views.py


注册应用
--------

将 ``django_oasis`` 应用添加到 Django 应用程序列表中。

.. code-block::
    :emphasize-lines: 5
    :caption: mysite/settings.py

    INSTALLED_APPS = [
        "django.contrib.admin",
        ...
        "myapp",
        "django_oasis",
    ]

.. note::
    这一步并不是必须的，如果你不需要使用 Oasis 提供的 API 文档模板，可以跳过这一步。但要完成此示例，必须注册 ``django_oasis``。


编写 API
----------

然后编写如下 API，它像 Django 的视图函数一样，负责处理请求并返回响应。

.. myliteralinclude:: ./views.py
    :caption: myapp/views.py


配置路由
--------

最后将 API 添加到 `OpenAPI <django_oasis.OpenAPI>` 实例中，并将 OpenAPI 实例的路由添加到 Django 路由配置中。

.. code-block::
    :caption: mysite/urls.py
    :emphasize-lines: 8-9,13-15

    from django.contrib import admin
    from django.urls import include, path
    from django_oasis import OpenAPI
    from django_oasis.docs import swagger_ui

    from myapp import views

    openapi = OpenAPI()
    openapi.add_resource(views.GreetingAPI)

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("", include(openapi.urls)),    # 这里将 OpenAPI 实例的路由设置在了根路由上 ("")，
                                            # 按照自己的需要可添加任意前缀路由 (如 "myapp/")。
        path("docs/", swagger_ui(openapi))  # 使用 Oasis 提供的 Swagger 模版用来查看 API 文档。
    ]


查看文档
--------

运行下面命令启动 Django 开发服务器

.. code-block:: bash

    $ python manage.py runserver

并访问 http://localhost:8000/docs/，将看到如下的文档页面。

.. openapiview:: ./views.py