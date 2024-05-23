from django.db import models

from django_oasis.common import model2schema
from django_oasis.core import Resource
from django_oasis.pagination import PagePagination

from .models import Book


@Resource("/books/page")
class BookListAPI:
    def get(
        self,
        pagination=PagePagination(model2schema(Book)),  # 设置分页器
    ):
        return pagination.paginate(Book.objects.all())  # 使用分页器
