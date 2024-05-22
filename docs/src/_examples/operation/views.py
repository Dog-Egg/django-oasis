from django_oasis import schema
from django_oasis.core import Operation, Resource


@Resource("/greeting")
class API:
    @Operation(
        summary="打个招呼",
        response_schema={
            "msg": schema.String(),
        },
    )
    def get(self):
        return {
            "msg": "Hello",
        }
