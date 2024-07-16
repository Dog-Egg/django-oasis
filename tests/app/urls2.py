"""
用于测试 swagger_ui 函数是否能找到路由中的 OpenAPI 实例，并解析其中的 OAS 输出地址
"""

from django.http import HttpResponse
from django.urls import include, path

from django_oasis.core import OpenAPI
from django_oasis.docs import swagger_ui

from . import views

openapi = OpenAPI()
openapi.add_resources(views)


def view(request):
    return HttpResponse()


sub_urlpatterns = [
    path("api/", include(openapi.urls)),
]

urlpatterns = [
    path("", view, name="index"),
    path("sub/", include((sub_urlpatterns, "sub"))),
    path("apidocs/", swagger_ui()),
]
