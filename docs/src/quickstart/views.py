from django_oasis import Resource


@Resource("/greeting")
class GreetingAPI:
    def get(self):
        return "Hello World"
