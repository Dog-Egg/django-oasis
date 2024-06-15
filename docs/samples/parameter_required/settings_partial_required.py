from django.urls import include, path

from django_oasis.core import OpenAPI

from . import views_partial_required

openapi = OpenAPI()
openapi.add_resources(views_partial_required)

urlpatterns = [path("", include(openapi.urls))]

ROOT_URLCONF = type("ROOT_URLCONF", (), {"urlpatterns": urlpatterns})
