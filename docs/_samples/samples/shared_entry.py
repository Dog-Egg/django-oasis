from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse
from django.views import View
import openapi
import zangar as z

from openapi.routing import Router


class FooAPI(View):
    @openapi.path("id", schema=z.to.int())
    @openapi.declare(tags=["bar"])
    def dispatch(self, request: HttpRequest, id) -> HttpResponse:
        return super().dispatch(request)

    @openapi.response(200)
    def put(self, request):
        return JsonResponse({})

    @openapi.response(204)
    def delete(self, request):
        return HttpResponse(204)


router = Router()
router.add_url("/foo/{id}", FooAPI)
