from django.http import HttpResponse

from django_oasis.core import Resource


@Resource("/api")
class API:
    def get(self):
        return "Hello World"


@Resource("/api")
class API:
    def get(self):
        return HttpResponse("Hello World")
