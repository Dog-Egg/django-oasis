import re

from openapi.spec import (
    DECLARED_PART_OAS,
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
        if hasattr(method_handle, DECLARED_PART_OAS):
            part = getattr(method_handle, DECLARED_PART_OAS)
            rv[method] = part

    return rv
