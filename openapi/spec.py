from __future__ import annotations as _annotations

import http as _http

import zangar as _z
from zangar import compilation as _compilation

OAS_DEFINITIONS = "oas_definitions"


class _SpecificObject:
    def __init__(self, **fields) -> None:
        self.__fields = fields

    @property
    def spec(self):
        return self.__fields


def define(obj: _SpecificObject | dict, /):
    def decorator(func):
        objs = getattr(func, OAS_DEFINITIONS, [])
        objs.append(obj)
        setattr(func, OAS_DEFINITIONS, objs)

        return func

    return decorator


def declare(**kwargs):
    return define(kwargs)


class ParameterObject(_SpecificObject):
    pass


class ResponseObject(_SpecificObject):
    def __init__(
        self,
        status_code: int,
        /,
        *,
        content: dict[str, MediaTypeObject] | None = None,
        description: str | None = None,
    ):
        self.status_code = status_code
        self.content = content
        self.description = description

    def spec(self):
        rv: dict = {
            "description": self.description
            or _http.HTTPStatus(self.status_code).phrase,
        }
        if self.content:
            rv["content"] = {
                content_type: content.spec()
                for content_type, content in self.content.items()
            }
        return rv


class RequestBodyObject(_SpecificObject):
    def __init__(
        self,
        *,
        content: dict[str, MediaTypeObject],
        required=False,
        **kwargs,
    ):
        self.content = content
        self.required = required
        super().__init__(
            **kwargs,
            content={
                content_type: content.spec()
                for content_type, content in content.items()
            },
            required=required,
        )


class MediaTypeObject:
    def __init__(self, *, schema: _z.Schema | None = None):
        self.schema = schema

    def spec(self):
        rv = {}
        if self.schema:
            rv["schema"] = _compilation.OpenAPI30Compiler().compile(self.schema)
        return rv
