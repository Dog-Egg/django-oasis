from django_oasis.core import Resource


@Resource("/greeting")
class GreetingAPI:
    def get(self):
        return "Hello World"
