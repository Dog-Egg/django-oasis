from django.http import HttpResponse

from django_oasis.core import Resource


@Resource("/api")
class API:
    def get(self):
        return None


@Resource("/api")
class API:
    def get(self):
        return HttpResponse()
