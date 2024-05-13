import functools
import inspect
import typing as t
import warnings

from .schemas import Schema
from .utils.hook import set_hook

__all__ = (
    "serialization_fget",
    "validator",
    "as_getter",
    "as_validator",
)


def as_getter(field: t.Union[Schema, str]):
    """
    自定义 `Model` 字段序列化时的取值函数。默认是对 `Mapping <collections.abc.Mapping>` 取索引，对其它对象取属性名。

    :param field: 字段或字段名，将取值函数应用于该字段。

    .. code-block::
        :emphasize-lines: 6

        >>> from django_oasis import schema

        >>> class Person(schema.Model):
        ...     fullname = schema.String()
        ...
        ...     @schema.as_getter(fullname)
        ...     def get_fullname(self, data):
        ...         return data['firstname'] + data['lastname']

        >>> Person().serialize({'firstname': '张', 'lastname': '三'})
        {'fullname': '张三'}
    """

    def decorator(method):
        return set_hook(
            method,
            lambda: (
                "as_getter",
                field._name if isinstance(field, Schema) else field,
            ),
            unique_within_a_single_class=True,
        )

    return decorator


def as_validator(field: t.Union[Schema, str, None, t.Callable] = None, /):
    """
    挂载验证函数。它会在调用验证时，执行其验证函数。

    :param field: 该参数用于验证 `Model` 字段。当设置为字段或字段名时，会将其验证函数应用于该字段，而不是 Model 自身。
    """

    def decorator(method, field=None):
        return set_hook(
            method,
            lambda: (
                "as_validator",
                field._name if isinstance(field, Schema) else field,
            ),
        )

    if inspect.isfunction(field):
        return decorator(field)
    return functools.partial(decorator, field=field)


def serialization_fget(*args, **kwargs):
    warnings.warn(
        f"Use {as_getter.__name__!r} instead of {serialization_fget.__name__!r}.",
        DeprecationWarning,
        stacklevel=2,
    )
    return as_getter(*args, **kwargs)


def validator(*args, **kwargs):
    warnings.warn(
        f"Use {as_validator.__name__!r} instead of {validator.__name__!r}.",
        DeprecationWarning,
        stacklevel=2,
    )
    return as_validator(*args, **kwargs)
