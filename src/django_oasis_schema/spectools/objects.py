import typing as t
from typing import Any

from django_oasis_schema import schemas

_CLEARN_INVALID_VALUES: t.List[t.Any] = [None, {}, []]


T = t.TypeVar("T", dict, list)


class Protect(t.Generic[T]):
    """保护最外层无效值不被 `clean` 清除。

    >>> clean({'schema': Protect({'type': None})})
    {'schema': {}}
    """

    def __init__(self, obj: T) -> None:
        self._obj: T = obj

    def __call__(self) -> T:
        return self._obj


class Skip(t.Generic[T]):
    """
    >>> clean({'schema': Skip({'type': None})})
    {'schema': {'type': None}}
    """

    def __init__(self, obj: T) -> None:
        self._obj: T = obj

    def __call__(self) -> T:
        return self._obj

    def __repr__(self) -> str:
        return f"skip: {self._obj!r}"


def clean(data: T) -> T:
    """
    >>> clean([{}, 0, None, [None], 1])
    [0, 1]
    """
    if isinstance(data, Skip):
        return data()

    if isinstance(data, dict):
        new = type(data)()
        for name, value in data.copy().items():
            protected = isinstance(value, Protect)
            if protected:
                value = value()
            value = clean(value)
            if protected or value not in _CLEARN_INVALID_VALUES:
                new[name] = value
        return new

    elif isinstance(data, list):
        new = type(data)()
        for value in data:
            protected = isinstance(value, Protect)
            if protected:
                value = value()
            value = clean(value)
            if protected or value not in _CLEARN_INVALID_VALUES:
                new.append(value)
        return new

    return data


class OpenAPISpec:
    """OpenAPI Specification 对象"""

    Protect = Protect
    Skip = Skip

    def __init__(self, *, info):
        self.__paths = {}
        self.__info = info
        self.__security_schemes = {}

    @property
    def title(self):
        return self.__info["title"]

    def add_path(self, path, pathitem):
        self.__paths[path] = pathitem

    def set_security_scheme(self, key, obj):
        if key not in self.__security_schemes:
            self.__security_schemes[key] = obj

    def to_dict(self):
        return clean(
            {
                "openapi": "3.0.3",
                "info": self.__info,
                "paths": self.__paths,
                "components": {
                    "securitySchemes": self.__security_schemes
                    and Skip(self.__security_schemes),
                },
            }
        )

    def parse(self, obj, **kwargs):
        try:
            return getattr(obj, "__openapispec__")(self, **kwargs)
        except TypeError as e:
            raise RuntimeError(obj, e)
