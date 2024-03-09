Hooks
=====

Hook 可以让 Schema 更加灵活好用，虽然它并不是实现的核心。它最初的目的是为了让 class 类和一些紧密相关的函数(不是指 method)以更加美观的方式组织在一起。


如下例所示，``validate_age`` 是与 ``User`` 相关的验证函数，但它却被定义在了全局域上，虽然毫无问题，但是代码结构并不好看。就好像只属于我的物品却被放在了公共展示柜里。

.. code-block::

    def validate_age(value):
        if value < 0:
            raise schema.ValidationError('年龄不能小于0。')

    class User(schema.Model):
        name = schema.String()
        age = schema.Integer(validators=[validate_age])


使用 hook 后，相关代码变得更加紧密，并且效果一样。

.. code-block::
    :emphasize-lines: 5

    class User(schema.Model):
        name = schema.String()
        age = schema.Integer()

        @schema.as_validator(age)  # 这是一个 hook
        def validate_age(self, value):
            if value < 0:
                raise schema.ValidationError('年龄不能小于0。')



由于 hook 被设计的很简单，所以它非常灵活，以致于可以代替实现很多 Schema 的功能。

使用用法
--------

hook 是以装饰器的形式定义在 Schema 类的方法上的。

.. testsetup:: *

    from django_oasis import schema


可用的 Hook
-----------

关于 `validator <django_oasis.schema.as_validator>` 的使用可在 :doc:`validation` 一章中查看。


Hook 的特点
-----------

不可调用
^^^^^^^^

虽然 hook 修饰的是类的方法，但是该方法并不像普通方法一样可以被调用。即无法使用 ``<class_name>.<method_name>`` 的方式进行调用。

.. testcode::

    class MySchema(schema.Schema):

        @schema.as_validator
        def hook_fn(self, value):
            ...

.. doctest::

    >>> MySchema.hook_fn
    Traceback (most recent call last):
        ...
    AttributeError: type object 'MySchema' has no attribute 'hook_fn'

这样做的目的是为了避免同名污染，你可以放心地为你的 hook 函数取任何函数名，它不会覆盖掉已有的同名方法。


不可重写
^^^^^^^^

hook 函数虽然是方法，但是它并不能在子类中被重写。


可继承
^^^^^^

父类的 hook 会继承给子类。

.. testcode::

    class Person(schema.Model):
        firstname = schema.String(write_only=True)
        lastname = schema.String(write_only=True)
        fullname = schema.String()

        @schema.as_getter(fullname)
        def get_fullname(self, data):
            return data['firstname'] + data['lastname']

    class Actor(Person):
        works = schema.List()


.. doctest::

    >>> Actor().serialize({'firstname': '赵', 'lastname': '四', 'works': ['乡村爱情']})
    {'fullname': '赵四', 'works': ['乡村爱情']}