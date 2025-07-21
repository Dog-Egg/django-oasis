from django.http import JsonResponse
from django.views import View
import openapi
from openapi.routing import Router

import zangar as z


class FooAPI(View):
    @openapi.parse_signature
    def get(self, request, a=openapi.s_query(schema=z.int())):
        return JsonResponse({})


router = Router()
router.add_url("/foo", FooAPI)
