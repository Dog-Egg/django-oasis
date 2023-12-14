from django_oasis import Resource, schema
from django_oasis.parameter import FormItem


@Resource("/to/path")
class API:
    def post(
        self,
        a=FormItem(schema.String()),
        b=FormItem(schema.Integer()),
    ):
        ...


from django_oasis import OpenAPI

openapi = OpenAPI(title="FormItem")
openapi.add_resource(API)
