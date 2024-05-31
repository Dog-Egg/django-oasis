from datetime import date

from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import QueryItem


@Resource("/api")
class API:
    def get(
        date=QueryItem(
            schema.Date(
                default=date.today,
            )
        )
    ): ...
