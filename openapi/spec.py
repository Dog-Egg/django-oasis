from __future__ import annotations as _annotations

import http as _http
from itertools import chain
import typing as _t
from functools import partial

import zangar as _z
from zangar import compilation as _compilation

_OAS_DEFINITIONS = "oas_definitions"
_HTTP_METHODS = [
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "head",
    # "options", # FIXME: django View 自带 options 方法，如果加入会出问题
    "trace",
]


def _set_response_schema(method, new, old):
    """OAS 设置 response schema 可能会冲突。

    这是个临时检查手段，后期考虑使用 merge 方式，如果遇到无法合并的问题再报错。
    """
    if old is not None and old != new:
        raise RuntimeError(f"Conflicting response schema for {method}", old, new)
    return new


def as_path_item_object(obj, /) -> dict:
    rv = {}

    # shared entry:
    shared_definitions = []
    for definition in getattr(obj.dispatch, _OAS_DEFINITIONS, []):
        if isinstance(definition, ParameterObject):
            _set_dict(rv, ["parameters"], lambda x: (x or []) + [definition.spec])
        else:
            shared_definitions.append(definition)

    # method entry
    for method in _HTTP_METHODS:
        if not hasattr(obj, method):
            continue

        method_handle = getattr(obj, method)
        method_definitions = getattr(method_handle, _OAS_DEFINITIONS, [])
        for definition in chain(reversed(method_definitions), shared_definitions):
            if isinstance(definition, ParameterObject):
                _set_dict(
                    rv,
                    [method, "parameters"],
                    lambda x: (x or []) + [definition.spec],
                )
            elif isinstance(definition, ResponseObject):
                _set_dict(
                    rv,
                    [method, "responses", str(definition.status_code)],
                    partial(_set_response_schema, method_handle, definition.spec()),
                )
            elif isinstance(definition, RequestBodyObject):
                _set_dict(rv, [method, "requestBody"], lambda _: definition.spec)
            else:
                assert isinstance(definition, dict), definition
                _set_dict(
                    rv,
                    [method],
                    lambda x: {**x, **definition} if x is not None else definition,
                )

    return rv


class _SpecificObject:
    def __init__(self, **fields) -> None:
        self.__fields = fields

    @property
    def spec(self):
        return self.__fields


def define(obj: _SpecificObject | dict, /):
    def decorator(func):
        objs = getattr(func, _OAS_DEFINITIONS, [])
        objs.append(obj)
        setattr(func, _OAS_DEFINITIONS, objs)

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


def _set_dict(
    data: dict, path: list[_t.Hashable], setter: _t.Callable[[_t.Any], _t.Any]
):
    d = data
    for index, key in enumerate(path):
        if index == len(path) - 1:
            d[key] = setter(d.get(key))
        else:
            d = d.setdefault(key, {})
    return data


class MediaTypeObject:
    def __init__(self, *, schema: _z.Schema | None = None):
        self.schema = schema

    def spec(self):
        rv = {}
        if self.schema:
            rv["schema"] = _compilation.OpenAPI30Compiler().compile(self.schema)
        return rv
