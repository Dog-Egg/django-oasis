Django-Oasis
============

Django-Oasis (后面简称 Oasis) 旨在更加高效地编写 HTTP API。


使用前提
--------

.. role:: color-necessary
.. role:: color-optional

* :color-necessary:`[必要]` 该项目基于 `Django <https://www.djangoproject.com>`_ 框架，所有在使用前需要对 Django 有基本的开发能力。
* :color-optional:`[可选]` 项目还使用了 `OpenAPI 规范 <https://spec.openapis.org/oas/v3.0.3>`_ (OAS) 来描述接口。它可以创建交互式接口文档，实现测试用例自动化，还能用于生成客户端代码等等。但不了解 OAS 也并不影响使用。


简单的示例
----------

这里定义了一个 ``Book`` 模型:

.. oasis-literalinclude:: demo models.py

并使用 Oasis 编写两个接口，为其实现 "查" 和 "增" 的功能:

.. oasis-literalinclude:: demo views.py

这些请求接口会被 Oasis 处理并转换为 Django 的视图函数和路由，这使其能够成为 Django 项目的一部分。并且还为接口生成了 OAS，将 OAS 导入文档生成工具 (如 SwaggerUI)，便可对外展示接口文档了。

这是由上面示例生成的 Swagger 文档：

.. oasis-swaggerui:: demo


功能说明
--------

* Oasis 使用自有的规则来编写接口代码，而不是使用 Django 的视图函数。
* Oasis 并不是生成文档，而是生成 OAS，OAS 可以用来做 API 文档和自动化测试使用。而且在整个开发过程中，几乎不需要手写 OAS。
* Oasis 内置了一个简单配置的 `swagger-ui <https://github.com/swagger-api/swagger-ui>`_，仅需几行代码即可查看接口文档。而且 Oasis 是以 HTTP 接口的形式暴露 OAS 数据，所以也可以选择喜欢的 API 可视化工具，或者自动化测试工具。
* Schema 是 Oasis 实现的核心，它负责定义数据结构，验证数据，并提供序列化及反序列化功能。


目录
----

.. toctree::
    :maxdepth: 2

    quickstart
    operations
    parameter_query
    parameter_header
    parameter_cookie
    parameter_path
    parameter_body
    response
    advanced/index
    upload_file
    pagination
    auth
    schema/index
    api

.. toctree::
    :caption: 示例
    :glob:

    examples/*
