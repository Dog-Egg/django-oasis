from django_oasis.core import Resource
from django_oasis.parameter import JsonData

from .schemas import BookSchema


@Resource("/book")
class BookAPI:
    def get(
        self,
        book=JsonData(
            BookSchema(required_fields=[]),
        ),
    ): ...
