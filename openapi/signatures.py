import functools
import inspect
import typing

import zangar as z

from .basic import Parameter, Query

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
            if param.default.py_default is not _MISSING:
                func = _inject_keyword_default(name, param.default.py_default)(func)
    return func


class SParameter:
    cls: type[Parameter]

    def __init__(
        self, py_default: typing.Any = _MISSING, *, schema: z.Schema, **kwargs
    ):
        self.schema = schema
        self.kwargs = kwargs
        self.py_default = py_default

    def create_parameter(self, name: str):
        return self.cls(
            name,
            schema=self.schema,
            **self.kwargs,
            required=self.py_default is _MISSING,
        )


class SQuery(SParameter):
    cls = Query


def s_query(
    *, schema: z.Schema[T], py_default: P | type[_MISSING] = _MISSING, **kwargs
) -> T | P:
    return typing.cast(T | P, SQuery(py_default, schema=schema, **kwargs))
