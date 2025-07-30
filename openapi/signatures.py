import functools
import inspect
import typing

import zangar as z

from .basic import Parameter, Path, Query

T = typing.TypeVar("T")
P = typing.TypeVar("P")


class _MISSING:
    pass


def _inject_keyword_default(kwname: str, default):
    def decorator(func):
        if inspect.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):  # type: ignore
                if kwname not in kwargs:
                    kwargs[kwname] = default
                return await func(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                if kwname not in kwargs:
                    kwargs[kwname] = default
                return func(*args, **kwargs)

        wrapper = functools.wraps(func)(wrapper)
        return wrapper

    return decorator


def apply_signature(func):
    sign = inspect.signature(func)
    for param in reversed(list(sign.parameters.values())):
        name = param.name
        if isinstance(param.default, SParameter):
            decorator = param.default.create_parameter(name)
            func = decorator(func)
            if (
                isinstance(param.default, SParameterWithDefault)
                and param.default.py_default is not _MISSING
            ):
                func = _inject_keyword_default(name, param.default.py_default)(func)
    return func


class SParameter:
    def __init__(self, cls: type[Parameter], /, **kwargs):
        self.cls = cls
        self.kwargs = kwargs

    def create_parameter(self, kwname: str):
        return self.cls(
            kwname,
            **self.kwargs,
        )


class SParameterWithDefault(SParameter):
    def __init__(self, cls: type[Parameter], py_default, /, **kwargs):
        super().__init__(cls, **kwargs)
        self.py_default = py_default


def s_query(
    *, schema: z.Schema[T], py_default: P | type[_MISSING] = _MISSING, **kwargs
) -> T | P:
    return typing.cast(
        T | P,
        SParameterWithDefault(
            Query, py_default, schema=schema, **kwargs, required=py_default is _MISSING
        ),
    )


def s_path(*, schema: z.Schema[T], **kwargs) -> T:
    return typing.cast(T, SParameter(Path, schema=schema, **kwargs, required=True))
