import functools
import http
import json
import typing
from inspect import iscoroutinefunction

import zangar as z
from django.http import HttpRequest, JsonResponse
from zangar.compilation import OpenAPI30Compiler

from openapi.utils import set_dict

from .spec import (
    MediaType,
    declare,
)


def response(
    status_code: int,
    /,
    *,
    content: dict[str, MediaType] | None = None,
    description: str | None = None,
):
    part: dict = {
        "description": description or http.HTTPStatus(status_code).phrase,
    }
    if content:
        part["content"] = {
            content_type: content_object.spec()
            for content_type, content_object in content.items()
        }

    def set_response(old_part):
        if old_part is not None and old_part != part:
            raise RuntimeError(
                f"Conflicting response schema for {status_code}", old_part, part
            )
        return part

    return declare(
        lambda spec: set_dict(spec, ["responses", str(status_code)], set_response)
    )


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


def _get_request(*args):
    for arg in args:
        if isinstance(arg, HttpRequest):
            return arg
    raise ValueError("No request found")


class Parameter:
    location: str

    def __init__(
        self,
        kwname: str | None,
        /,
        *,
        name: str | None = None,
        schema: z.Schema,
        required=True,
        **kwargs,
    ):
        if kwname is None and name is None:
            raise ValueError("name is required")
        self.kwname = kwname
        self.name = typing.cast(str, name or kwname)
        self.schema = schema
        self.required = required
        self.schema_object = _compile_schema(schema)

        self.parameter_object = {
            "name": self.name,
            "in": self.location,
            "schema": self.schema_object,
            "required": self.required,
        }
        self.parameter_object.update(kwargs)

    def process_request(self, request: HttpRequest):
        raise NotImplementedError

    MISSING_REQUIRED_PARAMETER_STATUS_CODE = 400
    PARAMETER_VALIDATION_ERROR_STATUS_CODE = 400

    def __call__(self, func):
        def parse_request(request):
            value = self.process_request(request)
            if value is _MISSING:
                if self.required:
                    raise ThrowValue(
                        JsonResponse(
                            {
                                "in": self.location,
                                "name": self.name,
                                "errors": "Missing required parameter",
                            },
                            status=self.MISSING_REQUIRED_PARAMETER_STATUS_CODE,
                        )
                    )
                return value
            try:
                return self.schema.parse(value)
            except z.ValidationError as e:
                raise ThrowValue(
                    JsonResponse(
                        {
                            "in": self.location,
                            "name": self.name,
                            "errors": e.format_errors(),
                        },
                        status=self.PARAMETER_VALIDATION_ERROR_STATUS_CODE,
                    )
                )

        if iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):  # type: ignore
                if self.kwname is not None:
                    if (value := parse_request(_get_request(*args))) is not _MISSING:
                        kwargs[self.kwname] = value
                return await func(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                if self.kwname is not None:
                    if (value := parse_request(_get_request(*args))) is not _MISSING:
                        kwargs[self.kwname] = value
                return func(*args, **kwargs)

        wrapper = functools.wraps(func)(wrapper)
        wrapper = catch_throw(wrapper)
        if self.required:
            wrapper = response(self.MISSING_REQUIRED_PARAMETER_STATUS_CODE)(wrapper)
        wrapper = response(self.PARAMETER_VALIDATION_ERROR_STATUS_CODE)(wrapper)
        wrapper = declare(
            lambda spec: set_dict(
                spec, ["parameters"], lambda x: [self.parameter_object] + (x or [])
            )
        )(wrapper)

        return wrapper


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


def query(*args, **kwargs):
    return Query(*args, **kwargs)


def header(*args, **kwargs):
    return Header(*args, **kwargs)


def path(*args, **kwargs):
    return Path(*args, **kwargs, required=True)


def body(kwname: str, /, content: dict[str, MediaType], required=True, **kwargs):
    request_body = dict(
        **kwargs,
        content={
            content_type: content.spec() for content_type, content in content.items()
        },
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

            async def wrapper(*args, **kwargs):  # type: ignore
                kwargs[kwname] = process_request_body(_get_request(*args))
                return await func(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                kwargs[kwname] = process_request_body(_get_request(*args))
                return func(*args, **kwargs)

        new_func = functools.wraps(func)(wrapper)
        new_func = catch_throw(new_func)
        new_func = response(400)(new_func)
        new_func = response(415)(new_func)
        new_func = declare(
            lambda spec: set_dict(spec, ["requestBody"], lambda _: request_body)
        )(new_func)
        return new_func

    return decorator
