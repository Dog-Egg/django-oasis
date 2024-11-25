from django_oasis import schema
from django_oasis.core import Resource


@Resource(
    "/files/{filepath}",
    param_schemas={"filepath": schema.Path()},
)
class API:
    def __init__(self, request, filepath): ...

    def get(self): ...
