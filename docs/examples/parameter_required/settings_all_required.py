from django.urls import include, path

from django_oasis.core import OpenAPI

from . import views_all_required

openapi = OpenAPI()
openapi.add_resources(views_all_required)

urlpatterns = [path("", include(openapi.urls))]

ROOT_URLCONF = type("ROOT_URLCONF", (), {"urlpatterns": urlpatterns})
