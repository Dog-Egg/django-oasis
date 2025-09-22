import functools
import inspect
import typing

import zangar as z

from .basic import Path, Query

T = typing.TypeVar("T")
P = typing.TypeVar("P")


class _MISSING:
    pass


def apply_signature(func):
    sign = inspect.signature(func)
    for param in reversed(list(sign.parameters.values())):
        name = param.name
        if isinstance(param.default, S):
            s = param.default
            func = s(name)(func)
    return func


class S:
    """
    等待 `apply_signature` 解析，使用函数签名来创建一个新的装饰器函数。

    @param creator: 一个可调用对象，接受一个参数 `name`，返回一个装饰器函数。
    @param default: 默认值，如果提供了这个参数，那么在调用函数时，如果参数没有提供，就会使用这个默认值。
    """

    def __init__(
        self,
        creator: typing.Callable[[str], typing.Callable],
        /,
        *,
        default: typing.Any = _MISSING,
    ):
        self.__creator = creator
        self.__default = default

    def __call__(self, name: str):
        def decorator(func):
            @self.__creator(name)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if name not in kwargs:
                    kwargs[name] = self.__default
                return func(*args, **kwargs)

            return wrapper

        return decorator


def s_query(
    *, schema: z.Schema[T], py_default: P | type[_MISSING] = _MISSING, **kwargs
) -> T | P:
    return typing.cast(
        T | P,
        S(
            lambda name: Query(
                name, schema=schema, **kwargs, required=py_default is _MISSING
            ),
            default=py_default,
        ),
    )


def s_path(*, schema: z.Schema[T], **kwargs) -> T:
    return typing.cast(
        T,
        S(lambda name: Path(name, schema=schema, **kwargs), default=_MISSING),
    )
