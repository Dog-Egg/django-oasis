from django.urls import include, path

from django_oasis.docs import swagger_ui

urlpatterns = [
    path("app1/", include("app1.urls")),
    path("app2/", include("app2.urls")),
    path("docs/", swagger_ui()),
]
