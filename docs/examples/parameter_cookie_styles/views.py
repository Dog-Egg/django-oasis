from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import CookieItem, Style


@Resource("/array/form/False")
class ArrayFormFalseAPI:
    def get(
        self,
        color=CookieItem(
            schema.List(schema.String()),
            Style("form", False),
        ),
    ):
        ...
        return color
