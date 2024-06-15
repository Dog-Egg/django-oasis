from django.urls import include, path

from django_oasis.core import OpenAPI

from .response_schema import API

openapi = OpenAPI()
openapi.add_resource(API)


urlpatterns = [
    path("", include(openapi.urls)),
]
