from __future__ import annotations as _annotations

import http as _http
import typing as _t
from functools import partial

import zangar as _z
from zangar import compilation as _compilation

_OAS_SPECIFIC_OBJECTS = "oas_specific_objects"
_OAS_DECLARATIONS = "oas_declarations"
_HTTP_METHODS = ["get", "post", "put", "delete", "patch", "head", "options", "trace"]


def _set_response_schema(method, new, old):
    """OAS 设置 response schema 可能会冲突。

    这是个临时检查手段，后期考虑使用 merge 方式，如果遇到无法合并的问题再报错。
    """
    if old is not None and old != new:
        raise RuntimeError(f"Conflicting response schema for {method}", old, new)
    return new


def as_path_item_spec(obj, /) -> dict:
    rv = {}

    for method in _HTTP_METHODS:
        if not hasattr(obj, method):
            continue

        method_handle = getattr(obj, method)
        method_specifics = getattr(method_handle, _OAS_SPECIFIC_OBJECTS, [])
        for specific in reversed(method_specifics):
            if isinstance(specific, ParameterObject):
                _set_dict(
                    rv,
                    [method, "parameters"],
                    lambda x: (x or []) + [specific.spec],
                )
            elif isinstance(specific, ResponseObject):
                _set_dict(
                    rv,
                    [method, "responses", str(specific.status_code)],
                    partial(_set_response_schema, method_handle, specific.spec()),
                )
            elif isinstance(specific, RequestBodyObject):
                _set_dict(rv, [method, "requestBody"], lambda _: specific.spec)
            else:
                raise NotImplementedError(f"Unknown specific object: {specific}")

        for operation_spec in getattr(method_handle, _OAS_DECLARATIONS, []):
            _set_dict(
                rv,
                [method],
                lambda x: {**x, **operation_spec} if x is not None else x,  # type: ignore
            )

    return rv


class _SpecificObject:
    def __init__(self, **fields) -> None:
        self.__fields = fields

    @property
    def spec(self):
        return self.__fields


def specify(specific: _SpecificObject, /):
    def decorator(func):
        objs = getattr(func, _OAS_SPECIFIC_OBJECTS, [])
        objs.append(specific)
        setattr(func, _OAS_SPECIFIC_OBJECTS, objs)

        return func

    return decorator


def declare(**kwargs):
    def decorator(obj):
        items = getattr(obj, _OAS_DECLARATIONS, [])
        items.append(kwargs)
        setattr(obj, _OAS_DECLARATIONS, items)

        return obj

    return decorator


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
