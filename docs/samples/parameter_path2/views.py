from django_oasis import schema
from django_oasis.core import Resource


@Resource(
    "/pets/{pet_id}",
    param_schemas={"pet_id": schema.Integer()},
)
class API:
    def __init__(self, request, pet_id): ...

    def get(self): ...
