from django_oasis.core import Operation, Resource
from django_oasis.parameter import JsonData

from .schemas import Model


@Resource("/api")
class API:
    @Operation(response_schema=Model)
    def post(
        self,
        data=JsonData(Model),
    ):
        a = data["attr"]  # I am here
        ...
