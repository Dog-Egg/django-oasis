from django.urls import include, path

from django_oasis.core import OpenAPI
from django_oasis.docs import swagger_ui

from . import views

openapi = OpenAPI()
openapi.add_resource(views.GreetingAPI)

urlpatterns = [
    path("myapi/", include(openapi.urls)),  # 注意这里需要用 `include` 函数
    path("docs/", swagger_ui(openapi)),  # 该路由用于查看 API 文档
]
