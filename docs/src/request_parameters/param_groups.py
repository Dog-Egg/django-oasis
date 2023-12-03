from django_oasis import Resource, schema
from django_oasis.parameter import Query


@Resource("/to/path")
class API:
    def get(
        self,
        q1=Query({"a": schema.String(), "b": schema.String()}),
        q2=Query({"c": schema.String()}),
    ):
        ...
