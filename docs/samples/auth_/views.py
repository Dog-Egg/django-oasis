from django_oasis.auth import IsAdministrator, IsAuthenticated
from django_oasis.core import Operation, Resource


@Resource("/to/path")
class API:
    @Operation(auth=IsAuthenticated)
    def get(self): ...

    @Operation(auth=IsAdministrator)
    def post(self): ...
