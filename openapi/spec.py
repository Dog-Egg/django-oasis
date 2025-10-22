from __future__ import annotations as _annotations

import typing

import zangar as _z
from zangar import compilation as _compilation

DECLARED_PART_OAS = "part_oas"


@typing.overload
def declare(update: typing.Callable[[dict], dict], /): ...


@typing.overload
def declare(**kwargs): ...


def declare(*args, **kwargs):
    if args:
        update = args[0]
    else:

        def update(value):
            return {**value, **kwargs}

    def decorator(func):
        value = getattr(func, DECLARED_PART_OAS, {})
        value = update(value)
        setattr(func, DECLARED_PART_OAS, value)

        return func

    return decorator


class MediaType:
    def __init__(self, *, schema: _z.Schema | None = None):
        self.schema = schema

    def spec(self):
        rv = {}
        if self.schema:
            rv["schema"] = _compilation.OpenAPI30Compiler().compile(self.schema)
        return rv
