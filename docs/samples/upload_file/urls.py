from django.urls import include, path

from django_oasis.core import OpenAPI

from . import multiple_files, single_file

openapi = OpenAPI()
openapi.add_resources(single_file)
openapi.add_resources(multiple_files)


urlpatterns = [
    path("", include(openapi.urls)),
]
