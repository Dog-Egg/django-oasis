from django_oasis.auth import IsAdministrator
from django_oasis.core import Operation, Resource


@Resource("/to/path")
class API:
    @Operation(auth=IsAdministrator)
    def get(self): ...
