from django_oasis.core import Resource, schema
from django_oasis.parameter import FormData


@Resource("/to/path")
class API:
    def post(
        self,
        form=FormData(
            {
                "a": schema.String(),
                "b": schema.Integer(),
            }
        ),
    ): ...
