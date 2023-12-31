from django_oasis import Resource, schema
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
    ):
        ...


from django_oasis import OpenAPI

openapi = OpenAPI(
    title="FormData",
)
openapi.add_resource(API)
