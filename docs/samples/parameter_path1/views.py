from django_oasis.core import Resource


@Resource("/pets/{pet_id}")
class API:
    def __init__(self, request, pet_id): ...

    def get(self): ...
