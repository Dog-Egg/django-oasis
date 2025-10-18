import pytest
import zangar as z
from django.http import JsonResponse
from django.test import override_settings
from django.urls import path

import openapi
from openapi.transformation import as_django_path, as_oas_path


class Namespace:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestSignatureParameters:
    def test_py_default(self, rf):
        @openapi.apply_signature
        def func(
            request, a=openapi.s_query(schema=z.to.int(), py_default=123, name="A")
        ):
            return a

        assert func(rf.get("/?A=1")) == 1
        assert func(rf.get("/")) == 123

    def test_s_path(self, client):
        @openapi.apply_signature
        def view(request, a=openapi.s_path(schema=z.to.int())):
            return JsonResponse({"a": a})

        with override_settings(
            ROOT_URLCONF=Namespace(
                urlpatterns=[
                    path("foo/<a>", view=view),
                ]
            )
        ):
            response = client.get("/foo/123")
            assert response.json() == {"a": 123}

    def test_s_body(self, rf):
        @openapi.apply_signature
        def view(
            request,
            body=openapi.s_body(
                content={
                    "application/json": openapi.MediaType(
                        schema=z.struct({"code": z.to.int()})
                    )
                }
            ),
        ):
            return body

        response = view(rf.post("/", {"code": "123"}, content_type="application/json"))
        assert response == {"code": 123}


class TestTransformation:
    paths = [
        ("/users/{user_id}", "/users/<user_id>", "/users/{user_id}"),
        ("/users/{int:user_id}", "/users/<int:user_id>", "/users/{user_id}"),
    ]

    @pytest.mark.parametrize("path", paths)
    def test_as_django_path(self, path):
        assert as_django_path(path[0]) == path[1]

    @pytest.mark.parametrize("path", paths)
    def test_as_oas_path(self, path):
        assert as_oas_path(path[0]) == path[2]
