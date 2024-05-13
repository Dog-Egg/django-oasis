from django_oasis.core import Resource, schema
from django_oasis.parameter import JsonData


@Resource("/to/path")
class API:
    def post(
        self,
        data=JsonData(
            {
                "a": schema.Integer(),
                "b": schema.String(),
            }
        ),
    ): ...


from django_oasis.core import OpenAPI

openapi = OpenAPI(title="JsonData")
openapi.add_resource(API)
