from django_oasis import Operation, Resource
from django_oasis.auth import IsAdministrator


@Resource("/to/path")
class API:
    @Operation(auth=IsAdministrator)
    def get(self):
        ...
