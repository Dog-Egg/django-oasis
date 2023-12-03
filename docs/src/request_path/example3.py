from django_oasis import Resource, schema


@Resource(
    "/files/{filepath}",
    param_schemas={"filepath": schema.Path()},
)
class API:
    def __init__(self, request, filepath):
        ...

    def get(self):
        ...
