import zangar as z
from django.http import JsonResponse
from django.views import View

import openapi
from openapi.routing import Router

bar_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n"]


def paginate(items, page, page_size):
    offset = (page - 1) * page_size
    return items[offset : offset + page_size]


class FooAPI(View):
    get_response_schema = z.struct(
        {
            "items": z.to.list(z.str()),
            "current_size": z.int(),
            "current_page_size": z.int(),
            "total": z.int(),
        }
    )

    @openapi.response(
        200, content={"application/json": openapi.MediaType(schema=get_response_schema)}
    )
    @openapi.apply_signature
    def get(
        self,
        request,
        page=openapi.s_query(schema=z.to.int().gte(1), py_default=1),
        page_size=openapi.s_query(schema=z.to.int().gte(1), py_default=10),
    ):
        return JsonResponse(
            self.get_response_schema.parse(
                {
                    "items": paginate(bar_list, page, page_size),
                    "current_size": page,
                    "current_page_size": page_size,
                    "total": len(bar_list),
                }
            )
        )


router = Router()
router.add_url("/foo", FooAPI)
