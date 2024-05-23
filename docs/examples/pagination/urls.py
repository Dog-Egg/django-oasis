from django.urls import include, path

from django_oasis.core import OpenAPI

from . import offset_pagination, page_pagination

openapi = OpenAPI()
openapi.add_resources(page_pagination)
openapi.add_resources(offset_pagination)


urlpatterns = [
    path("", include(openapi.urls)),
]
