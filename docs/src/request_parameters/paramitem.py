from django_oasis import Resource, schema
from django_oasis.parameter import QueryItem


@Resource("/to/path")
class API:
    def get(
        self,
        a=QueryItem(schema.Integer),
        b=QueryItem(schema.Integer(default=0)),
    ):
        ...
