from datetime import datetime

from django.http import JsonResponse

from django_oasis.core import Resource

from .response_schema import Book, BookSchema


@Resource("/api")
class API:
    def get(self):
        book = Book(
            title="The Book",
            created_at=datetime.now(),
        )
        data = BookSchema().serialize(book)
        return JsonResponse(data)
