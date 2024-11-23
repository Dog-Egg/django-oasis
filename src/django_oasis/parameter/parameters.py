from __future__ import annotations

import json
import re
import typing as t
import uuid
from collections import defaultdict

from django.http import HttpRequest
from django.utils.functional import cached_property

from django_oasis import schema as _schema
from django_oasis import schema as s
from django_oasis.exceptions import (
    BadRequestError,
    NotFoundError,
    RequestValidationError,
    UnsupportedMediaTypeError,
)
from django_oasis_schema.utils import make_model_schema, make_schema

from .style import Style, StyleHandler


class Path:
    """
    :param path: 到单个端点的相对路径，必须以正斜杠 ``/`` 开头。该路径将用于构建完整的 URL。支持 `路径模版 <https://spec.openapis.org/oas/v3.0.3#path-templating>`_ 。
    :param param_schemas: 路径中如果存在变量，则可以使用该值指定参数结构。变量默认结构为 `String <django_oasis.schema.String>`。
    :param param_styles: 路径中如果存在变量，则可以使用该值指定参数样式。
    """

    def __init__(
        self,
        path: str,
        /,
        param_schemas: t.Optional[t.Dict[str, _schema.Schema]] = None,
        param_styles: t.Union[t.Dict[str, Style], None] = None,
    ):
        if not path.startswith("/"):
            raise ValueError('The path must start with a "/".')
        self.__path = path
        self.__raw_param_schemas = param_schemas
        self.__raw_param_styles = param_styles
        self.__param_schemas: t.Dict[str, _schema.Schema] = {}
        self.__param_style_handlers: t.Dict[str, StyleHandler] = {}
        self.__resolved = False

    def _resolve(self) -> t.Tuple[str, str]:
        django_path = self.__path

        param_schemas = self.__raw_param_schemas or {}
        pattern = re.compile(r"{(?P<param>.*)}")
        for match in pattern.finditer(self.__path):
            (param,) = match.groups()
            if param not in param_schemas:
                param_schemas[param] = _schema.String()
            schema = param_schemas[param]
            self.__param_schemas[param] = schema

            if isinstance(schema, _schema.Path):
                placeholder = "<path:%s>"
            else:
                placeholder = "<%s>"
            django_path = django_path.replace(match.group(), placeholder % param)

            # style
            style = (self.__raw_param_styles or {}).get(param) or Style("simple", False)
            self.__param_style_handlers[param] = StyleHandler(style, schema, "path")

        self.__resolved = True
        return django_path, self.__path

    def parse_kwargs(self, kwargs: dict):
        if not self.__resolved:
            self._resolve()

        for param, schema in self.__param_schemas.items():
            if param not in kwargs:
                continue

            value = self.__param_style_handlers[param].handle(kwargs[param])
            try:
                kwargs[param] = schema.deserialize(value)
            except _schema.ValidationError:
                raise NotFoundError
        return kwargs

    def __openapispec__(self, oas):
        result = []
        for param, schema in self.__param_schemas.items():
            style = self.__param_style_handlers[param].style
            result.append(
                {
                    "name": param,
                    "in": "path",
                    "required": True,
                    "schema": schema.__openapispec__(oas),
                    "style": style.style,
                    "explode": style.explode,
                }
            )
        return result


class MountPoint:
    def setup(self, operation):
        pass

    def parse_request(self, request: HttpRequest):
        raise NotImplementedError

    def __openapispec__(self, oas):
        raise NotImplementedError


class RequestParameter(MountPoint):
    location: str

    def __init__(self, schema, /) -> None:
        self._schema = schema

    def parse_request(self, request: HttpRequest):
        try:
            return self._schema.deserialize(self._process_request(request))
        except s.ValidationError as e:
            raise RequestValidationError(e, self.location)

    def _process_request(self, request: HttpRequest):
        raise NotImplementedError


U = t.TypeVar("U")


class MountPointSet:
    def __init__(self, mountpints: dict[str, MountPoint]):
        self.__mountpints = mountpints

    def parse_request(self, request: HttpRequest):
        rv = {}
        for name, p in self.__mountpints.items():
            rv[name] = p.parse_request(request)
        return rv

    def __openapispec__(self, oas):
        rv = {}
        parameters = []
        for p in self.__mountpints.values():
            part = p.__openapispec__(oas)
            if isinstance(part, list):
                parameters.extend(part)
            else:
                rv.update(part)
        if parameters:
            rv.update(parameters=parameters)
        return rv


class RequestParameterWithStyle(RequestParameter):
    default_style: Style

    def __init__(self, schema, styles: dict[str, Style] | None = None) -> None:
        super().__init__(make_model_schema(schema))

        self.__styles = styles or {}
        self.__style_handlers: dict[s.Schema, StyleHandler] = {}
        for field in self._schema._fields.values():
            style = self.__get_style(field)
            self.__style_handlers[field] = StyleHandler(style, field, self.location)

    def __get_style(self, field: s.Schema) -> Style:
        if field._name in self.__styles:
            return self.__styles[field._name]
        return self.default_style

    def _process_request(self, request: HttpRequest):
        return self._process_style(self._get_request_data(request))

    def _get_request_data(self, request: HttpRequest):
        raise NotImplementedError

    def _process_style(self, data):
        rv = {}
        for field in self._schema._fields.values():
            handler = self.__style_handlers[field]
            v = handler.handle(data)
            if v is not handler.empty:
                rv[field._alias] = v
        return rv

    def __openapispec__(self, oas):
        parameters = []
        for field in self._schema._fields.values():
            style = self.__get_style(field)
            parameters.append(
                oas.ParameterObject(
                    {
                        "name": field._alias,
                        "in": self.location,
                        "required": field._required,
                        "description": oas.non_empty(field._description),
                        "schema": field.__openapispec__(oas),
                        "style": style.style,
                        "explode": style.explode,
                    }
                )
            )
        return parameters


class Query(RequestParameterWithStyle):
    """用于声明请求 query 的整体或是一部分。"""

    location = "query"
    default_style = Style("form", True)

    def _get_request_data(self, request):
        return request.GET


class Cookie(RequestParameterWithStyle):
    """用于声明请求 cookie 的整体或是一部分。"""

    location = "cookie"
    default_style = Style("form", False)

    def _get_request_data(self, request):
        return request.COOKIES


class Header(RequestParameterWithStyle):
    """用于声明请求 header 的整体或是一部分。"""

    location = "header"
    default_style = Style("simple", False)

    def _get_request_data(self, request):
        return request.headers


class RequestBodyParameter(RequestParameter):
    location = "body"
    content_type: str

    def parse_request(self, request):
        if request.content_type != self.content_type:
            raise UnsupportedMediaTypeError
        return super().parse_request(request)

    def __openapispec__(self, oas):
        return {
            "requestBody": {
                "required": True,
                "content": {
                    self.content_type: {
                        "schema": self._schema.__openapispec__(oas),
                    }
                },
            }
        }


class FormData(RequestBodyParameter):
    """用于声明表单请求的数据整体。"""

    def __init__(self, schema, /) -> None:
        super().__init__(make_model_schema(schema))

    @cached_property
    def content_type(self):
        for field in self._schema._fields.values():
            if isinstance(field, s.File) or (
                isinstance(field, s.List) and isinstance(field._item, s.File)
            ):
                return "multipart/form-data"
        return "application/x-www-form-urlencoded"

    def _process_request(self, request):
        data = {}
        for field in self._schema._fields.values():
            k = field._alias
            if isinstance(field, s.File) or (
                isinstance(field, s.List) and isinstance(field._item, s.File)
            ):
                target = request.FILES
            else:
                target = request.POST

            if k in target:
                if isinstance(field, s.List):
                    data[k] = target.getlist(k)
                else:
                    data[k] = target[k]
        return data


class JsonData(RequestBodyParameter):
    """用于声明 JSON 请求的数据整体。"""

    content_type = "application/json"

    def __init__(self, schema, /) -> None:
        super().__init__(make_schema(schema))

    def _process_request(self, request):
        try:
            return json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            raise BadRequestError("Invalid JSON data.")


## components


class RequestParameterComponent:
    @classmethod
    def build_request_parameter(
        cls: type[U], component_dict: dict[str, U]
    ) -> RequestParameter:
        raise NotImplementedError


class AssemblyWorker:
    def __init__(self, data: dict[str, RequestParameterComponent]) -> None:
        self.__components: dict[
            type[RequestParameterComponent], dict[str, RequestParameterComponent]
        ] = defaultdict(dict)
        for name, obj in data.items():
            self.__components[type(obj)][name] = obj

        self.__proxyname_and_namemap: list[tuple[str, list[tuple[str, str]]]] = []
        self.request_parameters: dict[str, RequestParameter] = {}
        for component_type, component_dict in self.__components.items():
            parameter = component_type.build_request_parameter(component_dict)
            proxy_name = f"${uuid.uuid4().hex}"
            self.__proxyname_and_namemap.append(
                (
                    proxy_name,
                    [
                        (name, field._attr)
                        for name, field in parameter._schema._fields.items()
                    ],
                )
            )
            self.request_parameters[proxy_name] = parameter

    def split(self, data: dict):
        data = data.copy()
        for proxyname, namemap in self.__proxyname_and_namemap:
            d = data.pop(proxyname)
            new_d = {}
            for n1, n2 in namemap:
                new_d[n1] = d.get(n2, s.undefined)
            data.update(new_d)
        return data


class RequestParameterComponentWithStyle(RequestParameterComponent):
    __request_parameter_cls__: type[RequestParameterWithStyle]

    def __init__(self, schema, style: Style | None = None):
        self.schema = make_schema(schema)
        self.style = style

    @classmethod
    def build_request_parameter(cls, component_dict):
        fields, styles = {}, {}
        for name, component in component_dict.items():
            fields[name] = component.schema
            if component.style is not None:
                styles[name] = component.style
        return cls.__request_parameter_cls__(fields, styles)


class QueryItem(RequestParameterComponentWithStyle):
    """用于声明请求 query 的单个字段。"""

    __request_parameter_cls__ = Query


class CookieItem(RequestParameterComponentWithStyle):
    """用于声明请求 cookie 的单个字段。"""

    __request_parameter_cls__ = Cookie


class HeaderItem(RequestParameterComponentWithStyle):
    """用于声明请求 header 的单个字段。"""

    __request_parameter_cls__ = Header


class RequestBodyParameterComponent(RequestParameterComponent):
    __request_parameter_cls__: type[RequestBodyParameter]

    def __init__(self, schema, /):
        self.schema = make_schema(schema)

    @classmethod
    def build_request_parameter(cls, component_dict):
        return cls.__request_parameter_cls__(
            {name: component.schema for name, component in component_dict.items()}
        )


class FormItem(RequestBodyParameterComponent):
    """用于声明表单请求的单个字段。"""

    __request_parameter_cls__ = FormData


class JsonItem(RequestBodyParameterComponent):
    """用于声明 JSON 请求的单个字段。"""

    __request_parameter_cls__ = JsonData


class MountPointSetWrapper:
    def __init__(self, data: dict[str, (MountPoint | RequestParameterComponent)]):
        _check_mountpoints(data.values())

        components = {}
        mountpoints = {}
        for name, obj in data.items():
            if isinstance(obj, RequestParameterComponent):
                components[name] = obj
            else:
                mountpoints[name] = obj
        self.__worker = AssemblyWorker(components)
        mountpoints.update(self.__worker.request_parameters)
        self.__mountpointset = MountPointSet(mountpoints)

    def parse_request(self, request: HttpRequest):
        results = self.__mountpointset.parse_request(request)
        return self.__worker.split(results)

    def __openapispec__(self, oas):
        return self.__mountpointset.__openapispec__(oas)


def _check_mountpoints(values: t.Iterable[MountPoint | RequestParameterComponent]):
    """
    FormItem, FormData, JsonItem, JsonData 不可共同存在，
    且 FormData 或 JsonData 只能存在一个。
    """
    unique_classes = {JsonData, FormData}
    mutex_classes = {FormItem, JsonItem} | unique_classes

    record = None
    for value in values:
        if value.__class__ not in mutex_classes:
            continue

        if record is None:
            record = value
            continue

        if record.__class__ != value.__class__:
            raise RuntimeError(
                f"{record.__class__.__name__} and {value.__class__.__name__} cannot be used together"
            )
        if record.__class__ == value.__class__ and record.__class__ in unique_classes:
            raise RuntimeError(
                f"{record.__class__.__name__} cannot be used more than once"
            )
