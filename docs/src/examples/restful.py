from django.db import models

from django_oasis.common import model2schema
from django_oasis.core import Operation, Resource
from django_oasis.exceptions import NotFoundError
from django_oasis.pagination import PagePagination
from django_oasis.parameter import Body


class Book(models.Model):
    title = models.CharField(max_length=50, verbose_name="标题")
    author = models.CharField(max_length=50, verbose_name="作者")


class BookSchema(model2schema(Book)):
    pass


@Resource("/books")
class BookListAPI:
    def get(
        self,
        pagination=PagePagination(BookSchema),
    ):
        return pagination.paginate(Book.objects.all())

    @Operation(
        response_schema=BookSchema,
        status_code=201,
    )
    def post(self, body=Body(BookSchema)):
        return Book.objects.create(**body)


@Resource("/books/{book_id}")
class BookItemAPI:
    def __init__(self, request, book_id):
        try:
            self.book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise NotFoundError

    @Operation(response_schema=BookSchema)
    def get(self):
        return self.book

    def update(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self.book, key, val)
        self.book.save()
        return self.book

    @Operation(response_schema=BookSchema)
    def put(
        self,
        body=Body(BookSchema(required_fields="__all__")),
    ):
        return self.update(**body)

    @Operation(response_schema=BookSchema)
    def patch(
        self,
        body=Body(BookSchema(required_fields=[])),
    ):
        return self.update(**body)

    @Operation(status_code=204)
    def delete(self):
        self.book.delete()
