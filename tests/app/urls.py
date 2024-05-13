from django.urls import include, path

from django_oasis.core import OpenAPI

from . import views

openapi = OpenAPI()
openapi.add_resources(views)


urlpatterns = [
    path("", include(openapi.urls)),
]
