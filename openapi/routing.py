import json
import os
import re

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.urls import path
from django.views import View

from .spec import as_path_item_spec

with open(os.path.join(os.path.dirname(__file__), "oas_schemas/v3.0.json")) as f:
    OAS_SCHEMA = json.load(f)
    del f


class Route:
    __regex = re.compile(r"^\{.*\}$")

    def __init__(self, route: str):
        self.__parts = [x for x in route.split("/") if x]

    def django_url(self):
        parts = []
        for part in self.__parts:
            if self.__regex.match(part):
                parts.append("<" + part[1:-1] + ">")
            else:
                parts.append(part)
        return "/".join(parts)

    def openapi_path(self):
        return "/" + "/".join(self.__parts)


class Router:
    openapi_endpoint = "openapi.json"

    def __init__(self) -> None:
        self.__openapi_paths: dict[str, dict] = {}
        self.__urls = [path(self.openapi_endpoint, self.__openapi_json, name="openapi")]

    def add_url(self, route: str, view: type[View]):
        assert route.startswith("/"), "Path must start with '/'"
        r = Route(route)
        self.__openapi_paths[r.openapi_path()] = as_path_item_spec(view)
        self.__urls.append(path(r.django_url(), view.as_view(), name=view.__name__))

    def spec(self):
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "API Document",
                "version": "0.1.0",
            },
            "paths": self.__openapi_paths,
        }

    def __openapi_json(self, request: HttpRequest):
        prefix = request.path.replace(self.openapi_endpoint, "")
        spec = self.spec()
        if prefix:
            spec.setdefault("servers", [{"url": prefix}])

        if settings.DEBUG:
            from jsonschema import validate

            validate(spec, OAS_SCHEMA)

        return JsonResponse(spec)

    @property
    def urls(self):
        return self.__urls
