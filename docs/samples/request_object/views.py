from django_oasis.core import Resource


@Resource("/path/to")
class API:
    def __init__(self, request):
        self.request = request

    def get(self):
        return f"Hello {self.request.user.username}"
