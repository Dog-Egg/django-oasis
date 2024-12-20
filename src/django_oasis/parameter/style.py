import typing as t

from django.http import QueryDict
from django.http.request import HttpHeaders
from django.utils.functional import cached_property

from django_oasis import schema as _schema


def _unchange(value):
    return value


def _split_by_comma(value):
    return value.split(",")


def _split_by_comma_object(value):
    """
    >>> _split_by_comma_object('R,100,G,150,B,200')
    {'R': '100', 'G': '150', 'B': '200'}
    """
    arr = value.split(",")
    return dict(zip(arr[::2], arr[1::2]))


def _split_by_comma_object2(value):
    """
    >>> _split_by_comma_object2('R=100,G=150,B=200')
    {'R': '100', 'G': '150', 'B': '200'}
    """
    return dict(map(lambda i: i.split("="), value.split(",")))


class StyleHandler:
    empty = object()

    def __init__(self, style: "Style", schema: _schema.Schema, location) -> None:
        self.schema = schema
        self.style = style
        self.location = location

        if self.key not in self.handlers:
            raise ValueError(f"{self.key} is not supported.")

    @cached_property
    def key(self):
        type = self.schema.meta["data_type"]
        if type not in {"array", "object"}:
            type = "primitive"
        return (self.location, self.style.style, self.style.explode, type)

    def handle(self, data):
        fn = self.handlers[self.key]
        fname = fn.__name__
        if hasattr(self, fname):
            return getattr(self, fname)(data)
        return fn(data)

    def _f1(self, data: QueryDict):
        return data.get(self.schema._alias, self.empty)

    def _f2(self, data: QueryDict):
        return data.getlist(self.schema._alias)

    def _f3(self, data: QueryDict):
        assert isinstance(self.schema, _schema.Model)
        rv = {}
        for f in self.schema._fields.values():
            if f._alias in data:
                rv[f._alias] = data[f._alias]
        return rv

    def _f4(self, data):
        if self.schema._alias not in data:
            return self.empty
        return data[self.schema._alias].split(",")

    def _f5(self, data: QueryDict):
        if self.schema._alias not in data:
            return self.empty
        return _split_by_comma_object(data[self.schema._alias])

    def _f6(self, data):
        if self.schema._alias not in data:
            return self.empty
        return data[self.schema._alias].split(" ")

    def _f7(self, data):
        if self.schema._alias not in data:
            return self.empty
        return data[self.schema._alias].split("|")

    def _f8(self, data: QueryDict):
        assert isinstance(self.schema, _schema.Model)
        rv = {}
        for f in self.schema._fields.values():
            k = f"{self.schema._alias}[{f._alias}]"
            if k in data:
                rv[f._alias] = data[k]
        return rv

    def _header_simple_array(self, data: HttpHeaders):
        assert isinstance(self.schema, _schema.List)
        alias = self.schema._alias
        value = data.get(alias)
        if value is None:
            return self.empty
        return value.split(",")

    def _header_simple_primitive(self, data: HttpHeaders):
        return data[self.schema._alias]

    handlers: t.Dict[t.Tuple, t.Callable] = {
        ("query", "form", True, "primitive"): _f1,
        ("query", "form", False, "primitive"): _f1,
        ("query", "form", True, "array"): _f2,
        ("query", "form", True, "object"): _f3,
        ("query", "form", False, "array"): _f4,
        ("query", "form", False, "object"): _f5,
        ("query", "spaceDelimited", False, "array"): _f6,
        ("query", "pipeDelimited", False, "array"): _f7,
        ("query", "deepObject", True, "object"): _f8,
        ("cookie", "form", False, "primitive"): _f1,
        ("cookie", "form", False, "array"): _f4,
        ("cookie", "form", False, "object"): _f5,
        ("path", "simple", False, "primitive"): _unchange,
        ("path", "simple", False, "array"): _split_by_comma,
        ("path", "simple", True, "array"): _split_by_comma,
        ("path", "simple", False, "object"): _split_by_comma_object,
        ("path", "simple", True, "object"): _split_by_comma_object2,
        ("header", "simple", False, "primitive"): _header_simple_primitive,
        ("header", "simple", False, "array"): _header_simple_array,
    }


class Style(t.NamedTuple):
    #: 描述如何根据参数值的类型序列化参数值。`查看详细说明 <https://spec.openapis.org/oas/v3.0.3#parameterStyle>`__
    style: str
    #: 当为 `True` 时，array或object类型的参数值为数组或映射的键值对的每个值生成单独的参数。对于其他类型的参数，此属性不起作用。`查看详细说明 <https://spec.openapis.org/oas/v3.0.3#parameterExplode>`__
    explode: bool
