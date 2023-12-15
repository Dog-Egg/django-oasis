import abc
import contextlib
import json
import re
import typing as t

from django.http import HttpRequest
from django.utils.datastructures import MultiValueDict
from django.utils.functional import cached_property

from django_oasis import schema as _schema
from django_oasis.exceptions import (
    BadRequestError,
    NotFoundError,
    RequestValidationError,
    UnsupportedMediaTypeError,
)
from django_oasis.spec.utils import default_as_none
from django_oasis_schema.spectools.utils import clean_commonmark
from django_oasis_schema.utils import make_instance, make_model_schema, make_schema

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

    def __openapispec__(self, spec):
        result = []
        for param, schema in self.__param_schemas.items():
            style = self.__param_style_handlers[param].style
            result.append(
                {
                    "name": param,
                    "in": "path",
                    "required": True,
                    "schema": spec.parse(schema),
                    "style": style.style,
                    "explode": style.explode,
                }
            )
        return result


class Parameter(abc.ABC):
    def setup(self, operation):
        pass

    @abc.abstractmethod
    def parse_request(self, request: HttpRequest):
        pass


class RequestData(Parameter, abc.ABC):
    location: str

    def parse_request(self, request: HttpRequest) -> t.Any:
        try:
            return self._parse_request(request)
        except _schema.ValidationError as exc:
            raise RequestValidationError(exc, self.location)

    @abc.abstractmethod
    def _parse_request(self, request):
        pass


class RequestParameter(RequestData, abc.ABC):
    def __init__(
        self,
        schema: t.Union[_schema.Model, t.Dict[str, _schema.Schema]],
        styles: t.Optional[t.Dict[str, Style]] = None,
    ):
        self._schema = make_model_schema(schema)

        self.__styles = styles or {}
        self.__style_handlers: t.Dict[_schema.Schema, StyleHandler] = {}
        for field in self._schema._fields.values():
            style = self.__get_style(field)
            self.__style_handlers[field] = StyleHandler(style, field, self.location)

    def __get_style(self, field: _schema.Schema) -> Style:
        if field._name in self.__styles:
            return self.__styles[field._name]

        if self.location == "query":
            return Style("form", True)
        elif self.location == "cookie":
            return Style("form", False)
        elif self.location == "header":
            return Style("simple", False)
        raise NotImplementedError(self.location)

    def _handle_style(self, data):
        rv = {}
        for field in self._schema._fields.values():
            handler = self.__style_handlers[field]
            v = handler.handle(data)
            if v is not handler.empty:
                rv[field._alias] = v
        return rv

    def __openapispec__(self, spec):
        result = []
        for field in self._schema._fields.values():
            style = self.__get_style(field)
            result.append(
                {
                    "name": field._alias,
                    "in": self.location,
                    "required": default_as_none(field._required, False),
                    "description": field._description or None,
                    "schema": spec.parse(field),
                    "style": style.style,
                    "explode": style.explode,
                    # "allowEmptyValue": default_as_none(field.allow_blank, False),
                    # "examples": field.examples,
                }
            )
        return dict(parameters=result)


class Query(RequestParameter):
    location = "query"

    def _parse_request(self, request: HttpRequest):
        return self._schema.deserialize(self._handle_style(request.GET))


class Cookie(RequestParameter):
    location = "cookie"

    def _parse_request(self, request: HttpRequest):
        return self._schema.deserialize(self._handle_style(request.COOKIES))


class Header(RequestParameter):
    location = "header"

    def _parse_request(self, request: HttpRequest):
        return self._schema.deserialize((request.headers))


class MediaType:
    def __init__(self, schema) -> None:
        self.__schema = make_schema(schema)

    def __openapispec__(self, spec):
        return {
            "schema": spec.parse(self.__schema),
        }

    def parse_request(self, request: HttpRequest):
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except (json.JSONDecodeError, TypeError):
                raise BadRequestError("Invalid Data")
        else:
            combine = MultiValueDict()
            combine.update(request.POST)
            combine.update(request.FILES)
            if isinstance(self.__schema, _schema.Model):
                data = {}
                for field in self.__schema._fields.values():
                    k = field._alias
                    if k in combine:
                        data[k] = (
                            combine.getlist(k)
                            if isinstance(field, _schema.List)
                            else combine[k]
                        )
            else:
                data = dict(combine.items())
        return self.__schema.deserialize(data)


class Body(RequestData):
    """
    声明 HTTP 请求体数据，默认数据格式类型为 JSON。

    :param content_type: 请求体内容类型，默认是: application/json。也可以设置为列表，以支持多种请求体类型。
    """

    location = "body"

    def __init__(
        self,
        schema,
        *,
        # content: t.Optional[t.Dict[str, MediaType]] = None,
        content_type: t.Union[str, t.List[str]] = "application/json",
        description: str = "",
        # required: bool = True,
    ):
        schema = make_schema(schema)

        if isinstance(content_type, str):
            content_type_list = [content_type]
        else:
            content_type_list = content_type

        self.__content: t.Dict[str, MediaType] = {
            item: MediaType(schema) for item in content_type_list
        }

        self.__required = True
        self.__description = clean_commonmark(description)

    def __openapispec__(self, spec):
        return {
            "requestBody": {
                "required": self.__required,
                "description": self.__description,
                "content": {c: spec.parse(m) for c, m in self.__content.items()},
            }
        }

    def _parse_request(self, request: HttpRequest):
        if request.content_type not in self.__content:
            raise UnsupportedMediaTypeError
        return self.__content[request.content_type].parse_request(request)


@contextlib.contextmanager
def _like_post_request(request):
    # 因为 django 不处理 POST 以外的表单数据，所以这个修改一下方法名
    method = request.method
    try:
        request.method = "POST"
        yield request
    finally:
        request.method = method


class RequestBodyContent(RequestData):
    location = "body"
    content_type: str

    def __init__(self, schema) -> None:
        self._schema = make_schema(schema)

    def __openapispec__(self, spec):
        return {
            "requestBody": {
                "required": True,
                "content": {
                    self.content_type: {
                        "schema": spec.parse(self._schema),
                    }
                },
            }
        }

    def parse_request(self, request: HttpRequest):
        if request.content_type != self.content_type:
            raise UnsupportedMediaTypeError
        return super().parse_request(request)


class JsonData(RequestBodyContent):
    """声明请求体数据，要求以 JSON 格式提交。"""

    content_type = "application/json"

    def __init__(
        self,
        schema: t.Union[
            _schema.Schema,
            t.Type[_schema.Schema],
            t.Dict[str, _schema.Schema],
        ],
    ) -> None:
        super().__init__(schema)

    def _parse_request(self, request):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            raise BadRequestError("Invalid JSON data.")
        return self._schema.deserialize(data)


class FormData(RequestBodyContent):
    """声明请求体数据，要求以表单格式提交。"""

    def __init__(
        self,
        schema: t.Union[
            _schema.Model,
            t.Type[_schema.Model],
            t.Dict[str, _schema.Schema],
        ],
        /,
    ) -> None:
        super().__init__(schema)
        assert isinstance(self._schema, _schema.Model)
        self._schema = t.cast(_schema.Model, self._schema)

    @cached_property
    def content_type(self):
        for field in self._schema._fields.values():
            if isinstance(field, _schema.File):
                return "multipart/form-data"
        return "application/x-www-form-urlencoded"

    def _parse_request(self, request: HttpRequest):
        data = {}
        for field in self._schema._fields.values():
            k = field._alias
            if isinstance(field, _schema.File):
                target = request.FILES
            else:
                target = request.POST
            if k in target:
                data[k] = target[k]
        return self._schema.deserialize(data)


class BaseItem(Parameter):
    def __init__(self, schema: t.Union[_schema.Schema, t.Type[_schema.Schema]]) -> None:
        self._schema = make_instance(schema)

    def parse_request(self, request: HttpRequest):
        result: dict = self._paramobj.parse_request(request)
        return result.popitem()[1]

    def __openapispec__(self, spec):
        return spec.parse(self._paramobj)

    def setitemname(self, name: str):
        self._paramobj = self._make_param_instance(name)

    def _make_param_instance(self, name: str):
        raise NotImplementedError


class ParamItem(BaseItem):
    _paramclass: t.Type[RequestParameter]

    def __init__(
        self,
        schema: t.Union[_schema.Schema, t.Type[_schema.Schema]],
        style: t.Optional[Style] = None,
    ) -> None:
        super().__init__(schema)
        self.__style = style

    def _make_param_instance(self, name):
        return self._paramclass(
            {name: self._schema}, {name: self.__style} if self.__style else None
        )


class QueryItem(ParamItem):
    _paramclass = Query


class HeaderItem(ParamItem):
    _paramclass = Header


class CookieItem(ParamItem):
    _paramclass = Cookie


class FormItem(BaseItem):
    """这是 `FormData` 的变体，用于声明表单中的一个键，而不是整个表单。"""

    def _make_param_instance(self, name: str):
        return FormData({name: self._schema})
