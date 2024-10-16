from django_oasis.core import Operation, Resource, schema


@Resource("/1", url_name="api1")
class API:

    @Operation(response_schema={"a": schema.Integer()})
    def get(self):
        return {"a": "a"}
