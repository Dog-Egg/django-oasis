from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import Query


@Resource("/api")
class API:
    def get(
        self,
        query=Query(
            {
                "a": schema.String(
                    erase=None,
                    required=False,
                ),
                "b": schema.String(required=False),
            },
        ),
    ):
        ...
        return query
