from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import HeaderItem, Style


@Resource("/array/simple/false")
class ArraySimpleFalseAPI:
    def get(
        self,
        color=HeaderItem(
            schema.List(schema.String()),
            Style("simple", False),
        ),
    ):
        ...
        return color
