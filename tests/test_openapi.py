import zangar as z
from django.http import JsonResponse
from django.test import override_settings
from django.urls import path

import openapi


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
