import re
import typing as _t
from functools import partial

from openapi.spec import (
    OAS_DEFINITIONS,
    ParameterObject,
    RequestBodyObject,
    ResponseObject,
)


def as_oas_path(path: str, /) -> str:
    """Convert a path to OpenAPI format."""

    # Pattern to match Django-style path parameters with type converters
    # Matches {type:name} and converts to {name}
    pattern = r"\{([^:}]+:)?([^}]+)\}"

    def replace_param(match):
        # Group 1 is the type converter (optional), Group 2 is the parameter name
        param_name = match.group(2)
        return f"{{{param_name}}}"

    return re.sub(pattern, replace_param, path)


def as_django_path(path: str, /) -> str:
    """Convert a path to Django format."""
    # Pattern to match OpenAPI-style path parameters
    # Matches {name} or {type:name} and converts to <name> or <type:name>
    pattern = r"\{([^}]+)\}"

    def replace_param(match):
        param_content = match.group(1)
        return f"<{param_content}>"

    return re.sub(pattern, replace_param, path)


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


def _set_response_schema(method, new, old):
    """OAS 设置 response schema 可能会冲突。

    这是个临时检查手段，后期考虑使用 merge 方式，如果遇到无法合并的问题再报错。
    """
    if old is not None and old != new:
        raise RuntimeError(f"Conflicting response schema for {method}", old, new)
    return new


_HTTP_METHODS = [
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "head",
    "options",
    "trace",
]


def as_path_item_object(obj, /) -> dict:
    rv = {}

    for method in _HTTP_METHODS:
        if not hasattr(obj, method):
            continue

        method_handle = getattr(obj, method)
        method_definitions = getattr(method_handle, OAS_DEFINITIONS, [])
        for definition in reversed(method_definitions):
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
