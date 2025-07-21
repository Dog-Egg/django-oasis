import inspect
import typing
from .basic import Parameter, Query, create_decorator
import zangar as z

T = typing.TypeVar("T")


def parse_signature(func):
    sign = inspect.signature(func)
    for name, param in sign.parameters.items():
        if isinstance(param.default, SParameter):
            decorator = create_decorator(name, param.default.create(name))
            func = decorator(func)
    return func


class SParameter:
    cls: type[Parameter]

    def __init__(self, *, schema: z.Schema, **kwargs):
        self.schema = schema
        self.kwargs = kwargs

    def create(self, name: str):
        return self.cls(
            name=name,
            schema=self.schema,
            **self.kwargs,
        )


class SQuery(SParameter):
    cls = Query


def s_query(*, schema: z.Schema[T], **kwargs) -> T:
    return typing.cast(T, SQuery(schema=schema, **kwargs))
