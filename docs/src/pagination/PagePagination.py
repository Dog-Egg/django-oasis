from django.db import models

from django_oasis import Resource, model2schema
from django_oasis.pagination import PagePagination


class Book(models.Model):
    title = models.CharField(max_length=10, verbose_name="书名")
    author = models.CharField(max_length=20, verbose_name="作者")


@Resource("/books")
class BookListAPI:
    def get(self, pagination=PagePagination(model2schema(Book))):
        return pagination.paginate(Book.objects.all())
