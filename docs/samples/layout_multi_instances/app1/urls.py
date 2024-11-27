from django.urls import include, path

from django_oasis.core import OpenAPI, Resource


@Resource("/api")
class API:
    def get(self): ...


openapi = OpenAPI(title="Document 1")
openapi.add_resource(API)

urlpatterns = [
    path("", include(openapi.urls)),
]
