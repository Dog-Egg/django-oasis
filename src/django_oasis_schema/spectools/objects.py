import typing as t
from collections import Counter

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
    if isinstance(data, ReferenceObject):
        # 还原
        data = data.jumps()

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

        self._components__schemas = {}
        self._reference_counter = Counter()

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
                    "schemas": self._components__schemas,
                },
            }
        )

    def parse(self, obj, **kwargs):
        try:
            definition = getattr(obj, "__openapispec__")(self, **kwargs)
        except TypeError as e:
            raise RuntimeError(obj, e)

        if isinstance(obj, ReferenceFlag):
            self._reference_counter.update([obj.__class__])
            return ReferenceObject(definition, obj.__class__, self)
        return definition


class ReferenceFlag:
    """用于统计 Schema 使用量的。
    同一类实例化对象数量超过一个，将使用 Reference Object ($ref) 进行引用。"""


class ReferenceObject:
    def __init__(self, definition: dict, klass: type, spec: OpenAPISpec) -> None:
        self.__definition = definition
        self.__klass = klass
        self.__spec = spec

    def jumps(self):
        definition = self.__definition.copy()
        if self.__spec._reference_counter[self.__klass] >= 2:
            required = definition.pop("required")

            schema_full_name = self.__klass.__module__ + "." + self.__klass.__qualname__
            self.__spec._components__schemas[schema_full_name] = {
                "title": self.__klass.__name__,
                **definition,
            }
            ref = {"$ref": f"#/components/schemas/{schema_full_name}"}
            if required:
                return {"allOf": [ref, {"required": required}]}
            return ref
        return definition
