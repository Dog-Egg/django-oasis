from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import QueryItem


@Resource("/api")
class API:
    def get(
        message=QueryItem(
            schema.String(
                default="Hi",
            )
        )
    ): ...
