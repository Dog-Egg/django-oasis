from django.http import JsonResponse
from django.views import View

import openapi
from openapi.routing import Router
import zangar as z


class FooAPI(View):
    @openapi.query("a", schema=z.int())
    def get(self, request, a: int):
        return JsonResponse({})


router = Router()
router.add_url("/foo", FooAPI)
