from __future__ import annotations

import copy
import functools
import hashlib
import inspect
import os
import sys
import typing as t
import warnings
from http import HTTPStatus

import django.urls
from build_openapispec import openapispec
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase, JsonResponse
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt

from django_oasis import schema
from django_oasis.auth import BaseAuth
from django_oasis.exceptions import (
    HTTPError,
    MethodNotAllowedError,
    RequestValidationError,
)
from django_oasis.parameter.parameters import (
    MountPoint,
    MountPointSetWrapper,
    Path,
    RequestParameterComponent,
)
from django_oasis_schema.utils import make_instance, make_model_schema, make_schema

__all__ = ("OpenAPI", "Resource", "Operation")


def _get_openapi_instance_id():
    frame = inspect.getframeinfo(sys._getframe(2))
    rv = "%s:%s" % (os.path.relpath(frame.filename), frame.lineno)
    return hashlib.md5(rv.encode()).hexdigest()[:8]


def handle_request_validation_error(e: RequestValidationError, request):
    return JsonResponse(
        {"validation_errors": e.exc.format_errors()},
        status=400,
    )


def handle_http_error(e: HTTPError, request):
    return JsonResponse(
        {
            "status_code": e.status_code,
            "reason": e.reason,
        },
        status=e.status_code,
    )


DEFAULT_ERROR_HANDLERS: t.Dict[t.Type[Exception], t.Callable] = {
    HTTPError: handle_http_error,
    RequestValidationError: handle_request_validation_error,
}


def _validate_oas(fn):
    def wrapper(*args, **kwargs):
        spec = fn(*args, **kwargs)

        if settings.DEBUG:
            try:
                from openapi_spec_validator import validate
            except ImportError:
                pass
            else:
                validate(spec)

        return spec

    return wrapper


class OpenAPI:
    """
    :param name: 如果需要对外分享 OAS 数据，建议设置该名称，它将作为 OAS 数据地址的一部分，而不是使用计算出的名称。

    """

    def __init__(
        self,
        *,
        title: str = "API Document",
        name: t.Optional[str] = None,
        description: t.Union[str, t.Callable[[HttpRequest], str]] = "",
    ):
        self.__title = title
        self.__description = description
        self.__urls: t.List[django.urls.URLPattern] = []

        id = _get_openapi_instance_id()
        self.__spec_endpoint = "/apispec_%s" % (name or id)
        self.__append_url(self.__spec_endpoint, self.spec_view, name=id)
        self.__error_handlers: t.Dict[t.Type[Exception], t.Callable] = (
            DEFAULT_ERROR_HANDLERS.copy()
        )
        self.__path_dict: dict[str, tuple[Resource, list[str]]] = {}

    @property
    def title(self):
        return self.__title

    def add_resources(self, module, **kwargs):
        """从模块中查找资源并添加。"""
        from django_oasis.utils.project import find_resources

        for res in find_resources(module):
            self.add_resource(res, **kwargs)

    def add_resource(self, obj, *, prefix="", tags: list[str] | None = None):
        if prefix:
            if not prefix.startswith("/") or prefix.endswith("/"):
                raise ValueError(
                    'The prefix must start with a "/" and cannot end with a "/".'
                )

        if isinstance(obj, Resource):
            resource = obj
        else:
            r = Resource.checkout(obj)
            if r is None:
                raise ValueError("%s is not marked by %s." % (obj, Resource.__name__))
            resource = r

        def handle_error(exc, *args, **kwargs):
            for cls in inspect.getmro(exc.__class__):
                if cls in self.__error_handlers:
                    handler = self.__error_handlers[cls]
                    return handler(exc, *args, **kwargs)
            raise exc

        resource._handle_error = handle_error

        django_path, openapi_path = resource._path._resolve()
        self.__append_url(
            prefix + django_path, resource.view_func, name=resource.url_name
        )
        self.__path_dict[prefix + openapi_path] = (resource, tags or [])

    def __append_url(self, path, *args, **kwargs):
        path = path.lstrip("/")
        self.__urls.append(django.urls.path(path, *args, **kwargs))

    @property
    def urls(self):
        return self.__urls

    @_validate_oas
    def get_spec(self, request: HttpRequest | None = None):
        oas = openapispec("3.0.3")

        if self.__description:
            if isinstance(self.__description, str):
                description = self.__description
            elif request:
                description = self.__description(request)
            else:
                description = oas.empty
        else:
            description = oas.empty

        if request:
            script_name = request.path[: -len(request.path_info)]
            if script_name:
                server = [{"url": script_name}]
            else:
                server = oas.empty
        else:
            server = oas.empty

        prefix = (
            request.path_info[: -len(self.__spec_endpoint)]
            if request is not None
            else ""
        )

        spec = oas.build(
            oas.OpenAPIObject(
                {
                    "info": oas.InfoObject(
                        {
                            "title": self.__title,
                            "version": "0.1.0",
                            "description": description,
                        }
                    ),
                    "paths": {
                        prefix + k: oas.PathItemObject(r.__openapispec__(oas, ts))
                        for k, (r, ts) in self.__path_dict.items()
                    },
                    "server": server,
                }
            )
        )

        return spec

    def spec_view(self, request: HttpRequest):
        spec = self.get_spec(request)
        json_dumps_params = dict(indent=2, ensure_ascii=False) if settings.DEBUG else {}
        return JsonResponse(spec, json_dumps_params=json_dumps_params)

    def register_schema(self, schema):
        schema = make_model_schema(schema)
        # schema.to_spec(self.id, need_required_field=True, schema_id=uuid.uuid4().hex)

    def error_handler(self, e: t.Type[Exception]):
        def decorator(fn):
            self.__error_handlers[e] = fn
            return fn

        return decorator


class Resource:
    """
    :param path: 资源 URL，必须以 "/" 开头。
    :param include_in_spec: 是否将当前资源解析到 OAS 中，默认为 `True`。
    :param default_auth: 为所属的 Operation 提供默认的 auth。
    :param url_name: 为 Django 提供 URL 命名。参考: `命名 URL 模式 <https://docs.djangoproject.com/en/5.0/topics/http/urls/#naming-url-patterns>`_
    """

    HTTP_METHODS = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
    ]

    _handle_error: t.Callable[[Exception, HttpRequest], HttpResponseBase]

    def __init__(
        self,
        path: str,
        *,
        param_schemas: t.Optional[t.Dict[str, schema.Schema]] = None,
        param_styles=None,
        tags=None,
        view_decorators: t.Optional[list] = None,
        url_name: t.Optional[str] = None,
        include_in_spec: bool = True,
        default_auth: t.Union[BaseAuth, t.Type[BaseAuth], None] = None,
    ):
        self._path: Path = Path(
            path, param_schemas=param_schemas, param_styles=param_styles
        )
        self.__url_name = url_name
        self.__operations: t.Dict[str, Operation] = {}
        self._tags: t.List = tags or []
        self.__view_decorators = view_decorators or []
        self.__include_in_spec = include_in_spec
        self._default_auth: t.Optional[BaseAuth] = (
            None if default_auth is None else make_instance(default_auth)
        )

    @property
    def url_name(self):
        return self.__url_name

    def __get_view_decorators(self):
        for d in self.__view_decorators:
            yield d

        def operation_decorator(source_decorator, http_method):
            def decorator(view):
                @functools.wraps(view)
                def wrapper(request, *args, **kwargs):
                    if request.method == http_method:
                        return source_decorator(view)(request, *args, **kwargs)
                    return view(request, *args, **kwargs)

                return wrapper

            return decorator

        for method, operation in self.__operations.items():
            for d in operation._view_decorators:
                yield operation_decorator(d, method.upper())

    __marked: t.Dict[t.Any, "Resource"] = {}

    def __call__(self, klass):
        if klass in self.__marked:
            raise ValueError(
                "%s has been marked by %s." % (klass, self.__class__.__name__)
            )
        self.__marked[klass] = self
        self.__klass = klass

        for method in self.HTTP_METHODS:
            handler = getattr(klass, method, None)
            if handler is None:
                continue

            operation = getattr(handler, "operation", None)
            if operation is None:
                operation = Operation()
                operation(handler)

            operation = copy.copy(operation)
            self.__operations[method] = operation

            assert operation._resource is None
            operation._resource = self

        return klass

    @classmethod
    def checkout(cls, obj) -> t.Optional["Resource"]:
        try:
            return cls.__marked.get(obj)
        except TypeError:
            return None

    @cached_property
    def view_func(self):
        @csrf_exempt
        def view(request, **kwargs) -> HttpResponseBase:
            try:
                rv, status_code = self.__view(request, **kwargs)
            except Exception as exc:
                if (
                    "django_oasis.middleware.ErrorHandlerMiddleware"
                    in settings.MIDDLEWARE
                ):
                    request._oasis_handle_error = self._handle_error
                    raise
                return self._handle_error(exc, request)
            return self.__make_response(rv, status_code)

        for decorator in self.__get_view_decorators():
            view = decorator(view)

        return view

    def __make_response(self, rv, status: int):
        if isinstance(rv, HttpResponseBase):
            return rv
        if rv is None:
            rv = b""
        if isinstance(rv, (str, bytes)):
            return HttpResponse(rv, status=status)
        return JsonResponse(rv, status=status, safe=False)

    def __view(self, request, **kwargs) -> t.Tuple[t.Any, int]:
        kwargs = self._path.parse_kwargs(kwargs)

        method = request.method.lower()
        if method in self.HTTP_METHODS and hasattr(self.__klass, method):
            instance = (
                self.__klass()
                if self.__klass.__init__ is object.__init__
                else self.__klass(request, **kwargs)
            )
            handler = getattr(instance, method)
        else:
            raise MethodNotAllowedError

        operation = self.__operations[method]
        return operation._wrapped_invoke(handler, request)

    def __openapispec__(self, oas, tags: list[str] | None = None) -> dict:
        if not self.__include_in_spec:
            return {}

        operations = {}
        path_params = self._path.__openapispec__(oas)
        for method, operation in self.__operations.items():
            operation_kwargs = operation.__openapispec__(oas, tags or [])
            if path_params:
                operation_kwargs.setdefault("parameters", []).extend(path_params)
            operations[method] = oas.OperationObject(operation_kwargs)
        return operations


class Operation:
    """
    :param include_in_spec: 是否将当前操作解析到 OAS 中，默认为 `True`。
    :param summary: 用于设置 OAS 操作对象摘要。
    :param auth: 设置操作请求认证。
    :param declare_responses: 声明可能的请求响应，用于构建 OAS。
    :param response_schema: 用于序列化请求操作返回值，并为 OAS 提供响应描述。

    .. deprecated:: 0.1
        view_decorators 是一个设计错误的参数，勿用。
    """

    def __init__(
        self,
        *,
        tags=None,
        summary: t.Optional[str] = None,
        description: t.Optional[str] = None,
        response_schema: t.Union[
            None, t.Type[schema.Model], t.Dict[str, schema.Schema], schema.Schema
        ] = None,
        deprecated: bool = False,
        include_in_spec: bool = True,
        auth: t.Union[BaseAuth, t.Type[BaseAuth], None] = None,
        status_code: int = 200,
        view_decorators: t.Optional[list] = None,
        declare_responses: t.Optional[dict] = None,
    ):
        self.__tags = tags or []
        self.__summary = summary
        self.__description = description

        self.response_schema: t.Optional[schema.Schema] = None
        if response_schema is not None:
            self.response_schema = make_schema(response_schema)

        self.__deprecated = deprecated
        self.__declare_responses = declare_responses
        self.__include_in_spec = include_in_spec
        self.__status_code = status_code
        self.__response_description = HTTPStatus(status_code).phrase
        self.__self_auth: t.Optional[BaseAuth] = (
            None if auth is None else make_instance(auth)
        )
        self._resource: t.Optional[Resource] = None
        self._view_decorators = view_decorators or []

        if view_decorators is not None:
            warnings.warn(
                "view_decorators is deprecated",
                DeprecationWarning,
            )

    __mountpointset: MountPointSetWrapper

    @property
    def __auth(self):
        if self._resource and self._resource._default_auth:
            return self._resource._default_auth
        return self.__self_auth

    def __parse_parameters(self, handler):
        ps: dict[str, MountPoint | RequestParameterComponent] = {}
        for name, parameter in inspect.signature(handler).parameters.items():
            obj = parameter.default
            if isinstance(obj, (MountPoint, RequestParameterComponent)):
                if isinstance(obj, MountPoint):
                    obj.setup(self)
                ps[name] = obj
        self.__mountpointset = MountPointSetWrapper(ps)

    def __call__(self, handler):
        self.__parse_parameters(handler)
        assert not hasattr(handler, "operation")
        handler.operation = self

        if self.__description is None:
            self.__description = inspect.getdoc(handler)

        return handler

    def _wrapped_invoke(self, handler, request) -> t.Tuple[t.Any, int]:
        if self.__auth:
            self.__auth.check_auth(request)

        kwargs = self.__mountpointset.parse_request(request)
        rv = handler(**kwargs)
        if not isinstance(rv, HttpResponseBase) and self.response_schema:
            try:
                rv = self.response_schema.serialize(rv)
            except Exception as e:
                raise ValueError(
                    f"{rv} cannot be serialized by {self.response_schema}."
                ) from e
        return rv, self.__status_code

    def __openapispec__(self, oas, tags: list[str]) -> dict:
        if not self.__include_in_spec:
            return {}

        other_responses = {}
        if self.__auth and hasattr(self.__auth, "declare_responses"):
            other_responses.update(self.__auth.declare_responses)

        if self.__declare_responses:
            other_responses.update(self.__declare_responses)

        if self.response_schema is not None:
            content = {
                "application/json": {
                    "schema": self.response_schema.__openapispec__(oas)
                }
            }
        else:
            content = oas.empty

        rv = {
            "summary": oas.non_empty(self.__summary),
            "description": oas.non_empty(self.__description),
            "tags": [
                *(self._resource._tags if self._resource else []),
                *self.__tags,
                *(tags or []),
            ]
            or oas.empty,
            "deprecated": self.__deprecated,
            "responses": {
                str(self.__status_code): oas.ResponseObject(
                    {
                        "description": self.__response_description,
                        "content": content,
                    }
                ),
                **{str(k): v for k, v in other_responses.items()},
            },
            "security": (
                [self.__auth.__openapispec__(oas)] if self.__auth else oas.empty
            ),
        }
        rv.update(self.__mountpointset.__openapispec__(oas))
        return rv
