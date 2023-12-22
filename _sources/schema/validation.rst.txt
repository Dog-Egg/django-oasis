验证数据
========

Schema 提供能多种验证方式。以下将以 “验证一个数是否为正整数” 为例，逐一介绍各个验证方式。


.. _use_validators:

使用参数
--------

这是最简单的验证方式。只需定义验证函数，并以参数的形式传递给 Schema 对象。

.. testcode::

    from django_oasis import schema

    def validate_positive_integer(value):
        """验证函数。"""
        if value <= 0:
            raise schema.ValidationError('这不是一个正整数.')


    obj = schema.Integer(validators=[validate_positive_integer])

    obj.deserialize(-1)    # 错误，将抛出异常。


.. testoutput::

    Traceback (most recent call last):
        ...
    django_oasis_schema.exceptions.ValidationError: [{'msgs': ['这不是一个正整数.']}]


使用 Hook
---------

`schema.validator <django_oasis.schema.validator>` 是一个专门挂载验证函数的 hook。

.. note::
    关于什么是 hook，详细请查看 :doc:`hooks` 章节。

如下示例所见，使用 `validator <django_oasis.schema.validator>` hook 后便无需传递验证函数，因为被修饰的验证函数会挂载到 Schema 的校验函数列表中。

.. testcode::

    class PositiveInteger(schema.Integer):

        @schema.validator
        def validate_value(self, value):
            if value <= 0:
                raise schema.ValidationError('不是一个正整数')

    PositiveInteger().deserialize(-1)

.. testoutput::

    Traceback (most recent call last):
        ...
    django_oasis_schema.exceptions.ValidationError: [{'msgs': ['不是一个正整数']}]

.. tip::
    validator hook 也是可以有多个的。

    .. testcode::

        class PositiveEvenInteger(schema.Integer):
            """正偶数：既要是正数，也要是偶数。"""

            @schema.validator
            def validate_value1(self, value):
                if value <= 0:
                    raise schema.ValidationError('不是一个整数')

            @schema.validator
            def validate_value2(self, value):
                if value % 2 != 0:
                    raise schema.ValidationError('不是一个偶数')


    .. doctest::

        >>> PositiveEvenInteger().deserialize(-3)
        Traceback (most recent call last):
            ...
        django_oasis_schema.exceptions.ValidationError: [{'msgs': ['不是一个整数', '不是一个偶数']}]


.. note::
    参数和 validator hook 可同时使用，它们的验证函数会合并后执行。

    .. doctest::

            >>> PositiveInteger(validators=[validate_positive_integer]).deserialize(-1)
            Traceback (most recent call last):
                ...
            django_oasis_schema.exceptions.ValidationError: [{'msgs': ['不是一个正整数', '这不是一个正整数.']}]


Model 验证
----------

Model 是有字段的，除了要验证 Model 本身外，还必须有能力验证其字段。当然，可以像 :ref:`use_validators` 给字段传入验证函数，这很简单，就不再介绍了。

这里任然要介绍 `schema.validator <django_oasis.schema.validator>` 这个 hook。它不仅能验证 Model 本身外，还能验证字段。只需要将字段传给这个 hook，它就会将其验证函数应用于该字段的验证。

举个例子，以下 Student 类的 ``age`` 字段需要验证其大于或等于 0。

.. testcode::

    class Student(schema.Model):
        name = schema.String()
        age = schema.Integer()

        @schema.validator(age) # 传入了字段 age
        def validate_age(self, value):
            if value < 0:
                raise schema.ValidationError('年龄必需大于0。')

    # 年龄错误，将抛出异常
    Student().deserialize({'name': '李华', 'age': -18})

.. testoutput::

    Traceback (most recent call last):
        ...
    django_oasis_schema.exceptions.ValidationError: [{'msgs': ['年龄必需大于0。'], 'loc': ['age']}]