Model Schema
============

Model 是一个包含 **字段** 的特殊 Schema，它用于声明具有属性的对象，**字段** 是以类属性的方式定义在 `schema.Model <django_oasis.schema.Model>` 子类中。Model 的用法如下：

.. testcode::

    from django_oasis import schema

    class Author(schema.Model):
        name = schema.String()


.. testsetup:: *

    from django_oasis import schema


Model 嵌套
-----------

将一个 Model 作为字段嵌套在其它 Model 中很简单。因为字段是一个 Schema，而 Model 本身也是 Schema，所以直接嵌套即可。

.. testcode::

    class Author(schema.Model):
        name = schema.String()
        birthday = schema.Date()

    class Book(schema.Model):
        title = schema.String()
        author = Author()

    print(Book().deserialize({'title': '三体', 'author': {'name': '刘慈欣', 'birthday': '1963-06-23'}}))

.. testoutput::

    {'title': '三体', 'author': {'name': '刘慈欣', 'birthday': datetime.date(1963, 6, 23)}}


.. _field:

字段
----

字段实际上也是一个 Schema 对象，只是当 Schema 对象作为 Model 的字段时，它便具备了字段的特性。下面将介绍字段的各种特性。


字段继承
^^^^^^^^

如同 Python 的类属性继承，Model 的字段同样也可以继承给子 Model。

单继承示例: B Model 继承于 A Model。

.. testcode::

    class A(schema.Model):
        a = schema.String()

    class B(A):
        b = schema.String()

    print(B().deserialize({'a': 1, 'b': 2}))

.. testoutput::

    {'a': '1', 'b': '2'}

多继承示例: C Model 同时继承 A Model 和 B Model。

.. testcode::

    class A(schema.Model):
        a = schema.String()

    class B(schema.Model):
        b = schema.String()

    class C(A, B):
        c = schema.String()

    print(C().deserialize({'a': 1, 'b': 2, 'c': 3}))

.. testoutput::

    {'a': '1', 'b': '2', 'c': '3'}

.. note::

    多继承时，如果多个父类存在同名字段，则优先继承位于左侧的父类的字段。

    .. testcode::

        class A1(schema.Model):
            a = schema.Integer()

        class A2(schema.Model):
            a = schema.String()

        class B1(A1, A2):
            ...

        class B2(A2, A1):
            ...

        value = {'a': 1}
        print(B1().deserialize(value))
        print(B2().deserialize(value))

    输出结果为：

    .. testoutput::

        {'a': 1}
        {'a': '1'}

字段命名要求
^^^^^^^^^^^^

你可能会想到如果字段名和父类的某个方法名或者属性同名时可能会导致错误的发生。

实际上并不会，虽然字段是以类属性的方式定义的，但字段并不会成为类属性，也就意味着无法通过 ``<model_name>.<field_name>`` 的形式访问到字段。

这样做的好处，就是不会出现同名污染，你可以为你的字段取任何名称，即便字段名为 "deserialize" 也不会发生错误。

.. doctest::

    >>> class Foo(schema.Model):
    ...     deserialize = schema.Integer()

    >>> Foo().deserialize({'deserialize': '1'})
    {'deserialize': 1}


alias 和 attr
^^^^^^^^^^^^^^

你可以用 alias 和 attr 参数为序列化和反序列化的两端指定不同的字段名映射。如果不指定，它们默认等于字段名。

它们之间的关系如下：

``attr`` --- *serialize()* ---> ``alias``

``alias`` --- *deserialize()* ---> ``attr``

参考示例：

.. doctest::

    >>> class Foo(schema.Model):
    ...     a = schema.Integer(alias='outside', attr='inside')

    >>> Foo().serialize({'inside': '1'})
    {'outside': 1}

    >>> Foo().deserialize({'outside': '1'})
    {'inside': 1}


clear_value
^^^^^^^^^^^

用于反序列化时，清除无意义的字段值。

默认定义了空白字符串为无意义值。如下所示: 字段 a 为必需，虽然反序列化时为其提供了一个空字符，但空字符串默认是无意义的，所以会在处理时被清除。

.. testcode::

    class Foo(schema.Model):
        a = schema.Integer(required=False)
        b = schema.Integer(required=False)

    print(Foo().deserialize({"a": "", "b": "2"}))


.. testoutput::

    {'b': 2}

自定义时需要为 ``clear_value`` 提供一个函数，函数返回 `True`，则值会被清除；返回 `False` 则不做处理。

.. testcode::

    # 把 0 作为无意义的值处理
    def clear_value(value):
        return value == 0

    class User(schema.Model):
        name = schema.String()
        age = schema.Integer(clear_value=clear_value, required=False)

    print(User().deserialize({'name': '李华', 'age': 0}))

.. testoutput::

    {'name': '李华'}

将 ``clear_value`` 设为 `None` 可以禁用此设置。

.. testcode::

    class Foo(schema.Model):
        a = schema.String(clear_value=None)

    print(Foo().deserialize({'a': ''}))

.. testoutput::

    {'a': ''}


.. note::
    ``clear_value`` 在处理 HTTP 请求 URL 参数时很有用。如: ``?a=&b=1`` 转字典后为 ``{'a': '', 'b': '1'}``，其中 a 参数的空字符串大多数情况下并无意义，所以应当被清除。
