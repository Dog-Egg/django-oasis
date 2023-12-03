from django_oasis import Resource


@Resource("/to/path")
class API:
    def __init__(self, request):
        self.request = request

    def get(self):
        print(self.request)
        # do something ...
