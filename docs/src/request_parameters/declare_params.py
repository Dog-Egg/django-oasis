from django_oasis import Resource, schema
from django_oasis.parameter import Query


class QuerySchema(schema.Model):
    a = schema.String()
    b = schema.Integer(default=1)


@Resource("/to/path")
class API:
    def get(self, query=Query(QuerySchema)):
        ...
