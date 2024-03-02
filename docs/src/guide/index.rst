指南
====

在 Django 中，请求 ( request ) 经过路由匹配 ( urlpatterns ) 到达对应的视图函数 ( view ) 进行处理，并最终返回响应 ( response )。Oasis 也正是对这一流程进行加工实现的。


关键概念
--------

回看之前的入门示例，有几个关键的概念需要说明。

.. code-block::

    @Resource("/greeting")
    class GreetingAPI:
        def get(self):
            return "Hello World"

* ``class GreetingAPI`` 是 API 类，它是一个普通的 Python 类，并且不需要特地继承指定的父类。
* `Resource <django_oasis.Resource>` 和 API 类共同组成了 Oasis 的请求资源。
* ``get`` 方法是一个请求操作，表示该请求资源可以处理 GET 请求，它是请求处理的单元。
* 请求操作上可以使用 `Operation <django_oasis.Operation>` 装饰对象，它为请求操作提供了更丰富的功能。


请求操作
--------

下例展示了所有支持的请求操作。

.. myliteralinclude:: ./operations.py

.. openapiview:: ./operations.py


Request 对象
-------------

在使用 Oasis 开发时，大多数时候都不需要直接使用到 Request 对象，所以请求操作并不像 Django 视图函数一样会接收到 Request 对象。

所以 Oasis 做了如下规定: 只有定义了 ``__init__`` 方法的 API 类才会接收到 Request 对象，且 Request 对象会以第一个位置参数的形式传递给 ``__init__`` 方法。该 Request 对象为 Django 的 `HttpRequest <https://docs.djangoproject.com/en/4.2/ref/request-response/#httprequest-objects>`_ 对象。

.. myliteralinclude:: ./request_object.py