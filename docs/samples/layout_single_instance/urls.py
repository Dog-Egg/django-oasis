from django.urls import include, path

from django_oasis.core import OpenAPI, Resource


@Resource("/api")
class API1:
    def get(self): ...


@Resource("/api")
class API2:
    def get(self): ...


openapi = OpenAPI()
openapi.add_resource(API1, prefix="/v1", tags=["v1"])
openapi.add_resource(API2, prefix="/v2", tags=["v2"])

urlpatterns = [
    path("", include(openapi.urls)),
]
