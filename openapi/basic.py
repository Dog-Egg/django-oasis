import functools
import json
from inspect import iscoroutinefunction

import zangar as z
from django.http import HttpRequest, JsonResponse
from zangar.compilation import OpenAPI30Compiler

from .spec import (
    MediaTypeObject,
    ParameterObject,
    RequestBodyObject,
    ResponseObject,
    specify,
)


def response(*args, **kwargs):
    return specify(ResponseObject(*args, **kwargs))


class ThrowValue(Exception):
    def __init__(self, value):
        self.value = value


def catch_throw(func):
    if iscoroutinefunction(func):

        @functools.wraps(func)
        async def awrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ThrowValue as e:
                return e.value

        return awrapper
    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ThrowValue as e:
                return e.value

        return wrapper


def _compile_schema(schema: z.Schema):
    return OpenAPI30Compiler().compile(schema)


class _MISSING:
    pass


class Parameter:
    location: str

    def __init__(
        self,
        /,
        *,
        name: str,
        schema: z.Schema,
        required=True,
        **kwargs,
    ):
        self.name: str = name
        self.schema = schema
        self.required = required
        self.schema_object = _compile_schema(schema)
        self.parameter_object = ParameterObject(
            **{
                "name": self.name,
                "in": self.location,
                "schema": self.schema_object,
                "required": self.required,
            },
            **kwargs,
        )

    def process_request(self, request: HttpRequest):
        raise NotImplementedError

    MISSING_REQUIRED_PARAMETER_STATUS_CODE = 400
    PARAMETER_VALIDATION_ERROR_STATUS_CODE = 400


def create_decorator(kwname: str | None, /, parameter: Parameter):
    def parse_request(request):
        value = parameter.process_request(request)
        if value is _MISSING:
            if parameter.required:
                raise ThrowValue(
                    JsonResponse(
                        {
                            "in": parameter.location,
                            "name": parameter.name,
                            "errors": "Missing required parameter",
                        },
                        status=parameter.MISSING_REQUIRED_PARAMETER_STATUS_CODE,
                    )
                )
            return value
        try:
            return parameter.schema.parse(value)
        except z.ValidationError as e:
            raise ThrowValue(
                JsonResponse(
                    {
                        "in": parameter.location,
                        "name": parameter.name,
                        "errors": e.format_errors(),
                    },
                    status=parameter.PARAMETER_VALIDATION_ERROR_STATUS_CODE,
                )
            )

    def decorator(func):
        if iscoroutinefunction(func):

            async def wrapper(_, request, *args, **kwargs):  # type: ignore
                if kwname is not None:
                    if (value := parse_request(request)) is not _MISSING:
                        kwargs[kwname] = value
                return await func(_, request, *args, **kwargs)

        else:

            def wrapper(_, request, *args, **kwargs):
                if kwname is not None:
                    if (value := parse_request(request)) is not _MISSING:
                        kwargs[kwname] = value
                return func(_, request, *args, **kwargs)

        wrapper = functools.wraps(func)(wrapper)
        wrapper = catch_throw(wrapper)
        if parameter.required:
            wrapper = response(parameter.MISSING_REQUIRED_PARAMETER_STATUS_CODE)(
                wrapper
            )
        wrapper = response(parameter.PARAMETER_VALIDATION_ERROR_STATUS_CODE)(wrapper)
        wrapper = specify(parameter.parameter_object)(wrapper)

        return wrapper

    return decorator


class Query(Parameter):
    location = "query"

    def process_request(self, request: HttpRequest):
        # object type
        if self.schema_object["type"] == "object":
            return request.GET

        # array type
        if self.schema_object["type"] == "array":
            return request.GET.getlist(self.name)

        # primitive type
        if self.name not in request.GET:
            return _MISSING
        return request.GET[self.name]


class Header(Parameter):
    location = "header"
    MISSING_REQUIRED_PARAMETER_STATUS_CODE = 406

    def process_request(self, request: HttpRequest):
        if self.name not in request.headers:
            return _MISSING
        return request.headers[self.name]


class Path(Parameter):
    location = "path"

    PARAMETER_VALIDATION_ERROR_STATUS_CODE = 404

    def process_request(self, request: HttpRequest):
        assert request.resolver_match is not None
        return request.resolver_match.kwargs[self.name]


def _decorator_factory(param_class: type[Parameter], kwname: str | None, /, **kwargs):
    if kwargs is not None:
        kwargs.setdefault("name", kwname)
    return create_decorator(kwname, param_class(**kwargs))


def query(*args, **kwargs):
    return _decorator_factory(Query, *args, **kwargs)


def header(*args, **kwargs):
    return _decorator_factory(Header, *args, **kwargs)


def path(*args, **kwargs):
    return _decorator_factory(Path, *args, **kwargs, required=True)


def body(kwname: str, /, content: dict[str, MediaTypeObject], required=True, **kwargs):
    request_body = RequestBodyObject(
        **kwargs,
        content=content,
        required=required,
    )

    def process_request_body(request: HttpRequest):
        if request.content_type not in content:
            raise ThrowValue(
                JsonResponse(
                    {
                        "errors": f"Unsupported content type: {request.content_type}",
                    },
                    status=415,
                )
            )

        if request.content_type == "application/json":
            try:
                arg = json.loads(request.body)
            except json.JSONDecodeError:
                raise ThrowValue(
                    JsonResponse(
                        {
                            "errors": "Invalid JSON",
                        },
                        status=400,
                    )
                )

        if request.content_type == "application/x-www-form-urlencoded":
            arg = request.POST

        schema = content[request.content_type].schema
        if not schema:
            return arg

        try:
            return schema.parse(arg)
        except z.ValidationError as e:
            raise ThrowValue(
                JsonResponse(
                    {
                        "in": "body",
                        "errors": e.format_errors(),
                    },
                    status=400,
                )
            )

    def decorator(func):
        if iscoroutinefunction(func):

            async def wrapper(_, request, *args, **kwargs):  # type: ignore
                kwargs[kwname] = process_request_body(request)
                return await func(_, request, *args, **kwargs)

        else:

            def wrapper(_, request, *args, **kwargs):
                kwargs[kwname] = process_request_body(request)
                return func(_, request, *args, **kwargs)

        new_func = functools.wraps(func)(wrapper)
        new_func = catch_throw(new_func)
        new_func = response(400)(new_func)
        new_func = response(415)(new_func)
        new_func = specify(request_body)(new_func)
        return new_func

    return decorator
