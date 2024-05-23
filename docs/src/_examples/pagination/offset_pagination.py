from django.db import models

from django_oasis.common import model2schema
from django_oasis.core import Resource
from django_oasis.pagination import OffsetPagination

from .models import Book


@Resource("/books/offset")
class BookListAPI:
    def get(
        self,
        pagination=OffsetPagination(model2schema(Book)),  # 设置分页器
    ):
        return pagination.paginate(Book.objects.all())  # 使用分页器
