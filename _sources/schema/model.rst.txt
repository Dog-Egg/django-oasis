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

你可以使用任何有效的字段名，即使字段名和父类的某个方法名或者属性同名也不会导致错误。

虽然字段是以类属性的方式定义的，但字段并不会成为类属性，也就意味着无法通过 ``<model_name>.<field_name>`` 的形式访问到字段。

这样做的好处，就是不会出现同名污染，如下例字段名为 "deserialize"，这和 `Schema.deserialize <django_oasis.schema.Schema.deserialize>` 方法同名，但这并不会有任何问题。

.. doctest::

    >>> class Foo(schema.Model):
    ...     deserialize = schema.Integer()

    >>> Foo().deserialize({'deserialize': '1'})
    {'deserialize': 1}


alias 和 attr
^^^^^^^^^^^^^^

可以使用 alias 和 attr 参数为序列化和反序列化的两端指定不同的字段名映射。如果不指定，它们默认等于字段名。

它们之间的关系如下：

attr --- *serialize()* ---> alias

alias --- *deserialize()* ---> attr

示例：

.. doctest::

    >>> class Foo(schema.Model):
    ...     a = schema.Integer(alias='outside', attr='inside')

    >>> Foo().serialize({'inside': '1'})
    {'outside': 1}

    >>> Foo().deserialize({'outside': '1'})
    {'inside': 1}
