介绍
====

Django-Oasis (后面简称 Oasis) 旨在帮助开发者使用 Django 高效地编写 HTTP API。

前提
----

该项目基于 Django 框架，并使用 OpenAPI-Specification v3.0.3 定义接口。在开始之前，你需要学习 Django 和 OpenAPI 规范的相关知识，因为本文档中并未对涉及它们的概念和功能做详细的说明。

所以如果你还不了解 Django 和 OpenAPI 规范，你可能会对文档中的内容感到一头雾水。先去学习它们，之后再回到这里。

* `Django <https://www.djangoproject.com>`_: Django 是一个高级 Python Web 框架，鼓励快速开发和简洁、务实的设计。它由经验丰富的开发人员构建，解决了 Web 开发的大部分麻烦，因此您可以专注于编写应用程序，而无需重新发明轮子。
* `OpenAPI 规范 <https://spec.openapis.org/oas/v3.0.3>`_: OpenAPI 规范 (OAS) 定义了一个与语言无关的标准 HTTP API 接口，允许人类和计算机发现和理解服务的功能，而无需访问源代码、文档或通过网络流量检查。

示例
----

以下是一个简单的示例，帮助你快速了解 Oasis 能做什么？

示例中定义了一个 ``BookModel``，并使用 Oasis 编写两个接口，为其实现 "查" 和 "增" 的功能。

.. literalinclude:: ./index_demo.py

以上定义的接口会被 Oasis 处理并转换为 Django 的视图函数和路由，这使其能够成为 Django 项目的一部分。并且还为接口生成了 OAS，将 OAS 导入文档生成工具 (如 SwaggerUI)，便可对外展示接口文档了。

这是由上面示例生成的 Swagger 文档：

.. openapiview:: ./index_demo.py


功能说明
--------

* Oasis 使用自有的规则来编写接口代码，而不是使用 Django 的视图函数。
* Oasis 并不是生成文档，而是生成 OAS，OAS 可以用来做 API 文档和自动化测试使用。而且在整个开发过程中，几乎不需要手写 OAS。
* Oasis 内置了一个简单配置的 `swagger-ui <https://github.com/swagger-api/swagger-ui>`_，仅需几行代码即可查看自己的接口文档。而且 Oasis 是以 HTTP 接口的形式暴露 OAS 数据，所以你也可以选择自己喜欢的 API 可视化工具，或者自动化测试工具。
* Schema 是 Oasis 实现的核心，它负责定义数据结构，验证数据，并提供序列化及反序列化功能。接下来的文档会有较多的内容说明 Schema 的功能。


关于文档
--------

后面文档中的 HTTP API 示例下基本都会跟随一个 Swagger 文档展示，该 Swagger 文档也是使用 Oasis 解析示例代码获得的，这可以帮助你更直观地查看示例代码被解析为 OAS 后的效果。


内容目录
--------

.. toctree::
    :maxdepth: 2

    quickstart/index
    guide/index
    request_parameters/index
    request_path/index
    request_body/index
    pagination/index
    schema/index
    api

.. toctree::
    :caption: 示例

    ./examples/restful
