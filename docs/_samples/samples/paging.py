from dataclasses import dataclass, field

import zangar as z
from django.http import JsonResponse
from django.views import View

import openapi
from openapi.routing import Router


@dataclass
class Paging:
    page: int = field(default=1, metadata={"zangar": {"schema": z.to.int().gte(1)}})
    page_size: int = field(
        default=10, metadata={"zangar": {"schema": z.to.int().gte(1)}}
    )

    def paginate(self, items):
        offset = (self.page - 1) * self.page_size
        return items[offset : offset + self.page_size]


bar_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n"]


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
        paging=openapi.s_query(
            schema=z.dataclass(Paging),
            py_default=Paging(),
        ),
    ):
        return JsonResponse(
            self.get_response_schema.parse(
                {
                    "items": paging.paginate(bar_list),
                    "current_size": paging.page,
                    "current_page_size": paging.page_size,
                    "total": len(bar_list),
                }
            )
        )


router = Router()
router.add_url("/foo", FooAPI)
