Schema
======

Schema 用于声明数据的类型、结构及验证规则等，并提供了序列化及反序列化的功能。Schema 可以声明一个整数，或是列表，还可以是一个复杂的对象。按照功能功能划分，本文档将 Schema 的说明分为 :doc:`./model` 和一般 Schema。

本篇内容将介绍 Schema 的通用功能。

.. toctree::
    :hidden:

    model
    validation

.. testsetup::

    from django_oasis import schema

序列化
------

序列化的目的是为了将 Python 对象转换为外部可识别的数据。

Schema 可以序列化一个简单的数据类型：

.. doctest::

    >>> from django_oasis import schema
    >>> from datetime import datetime

    >>> schema.Datetime().serialize(datetime(2023, 1, 1))
    '2023-01-01T00:00:00'

也可以是一个复杂的对象：

.. doctest::

    >>> class UserSchema(schema.Model):
    ...     name = schema.String()
    ...     created_at = schema.Datetime()

    >>> UserSchema().serialize({'name': '张三', 'created_at': datetime(2023, 1, 1)})
    {'name': '张三', 'created_at': '2023-01-01T00:00:00'}


反序列化
--------

这是序列化的逆向操作，即将一个数据转换为 Python 对象。

.. doctest::

    >>> schema.Datetime().deserialize('2023-01-01T00:00:00')
    datetime.datetime(2023, 1, 1, 0, 0)

    >>> UserSchema().deserialize({'name': '张三', 'created_at': '2023-01-01'})
    {'name': '张三', 'created_at': datetime.datetime(2023, 1, 1, 0, 0)}

在反序列化的过程中会对数据进行验证，稍后会在 :doc:`./validation` 章节做详细说明。


choices
-------

验证值是否等于选项序列中的一个。该序列中的元素应该是唯一的。

若值在选项内，将正常输出:

.. testcode::

    fruit = schema.String(choices=['apple', 'watermelon', 'grape'])

    print(fruit.deserialize('apple'))

.. testoutput::

    apple

若值不在选项内，将抛出异常：

.. testcode::

    fruit.deserialize('banana')

.. testoutput::

    Traceback (most recent call last):
        ...
    django_oasis_schema.exceptions.ValidationError: [{'msgs': ["The value must be one of 'apple', 'watermelon', 'grape'."]}]

.. note::
    OAS: 该参数会映射为 `enum <https://json-schema.org/draft/2020-12/json-schema-validation#name-enum>`_ 关键字。


after_deserialization
---------------------

反序列化后置处理函数。

如用于去除字符串前后多余的空白符:

.. testcode::

    email = schema.String(after_deserialization=str.strip)
    print(repr(email.deserialize('123@example.com  ')))

.. testoutput::

    '123@example.com'
