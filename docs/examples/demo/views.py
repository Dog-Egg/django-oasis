from django_oasis.common import model2schema
from django_oasis.core import Operation, Resource
from django_oasis.pagination import PagePagination
from django_oasis.parameter import Body

from .models import Book


# Oasis 并不能直接理解 Django Model 中的定义，
# 所以需要使用 `model2schema` 将 Book 模型转换成 Schema。
class BookSchema(model2schema(Book)):
    pass


@Resource("/books")
class BookListAPI:
    # get 方法负责处理 GET 请求，用于查询 Book
    def get(self, pagination=PagePagination(BookSchema)):
        # 这里使用了 Oasis 提供的分页功能
        return pagination.paginate(Book.objects.all())

    # post 方法负责处理 POST 请求，用于新增 Book
    @Operation(response_schema=BookSchema)
    def post(self, data=Body(BookSchema)):
        return Book.objects.create(**data)
