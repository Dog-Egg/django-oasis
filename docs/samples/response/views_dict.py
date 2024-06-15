from django.http import JsonResponse

from django_oasis.core import Resource


@Resource("/api")
class API:
    def get(self):
        return {"message": "Hello World"}


@Resource("/api")
class API:
    def get(self):
        return JsonResponse({"message": "Hello World"})
