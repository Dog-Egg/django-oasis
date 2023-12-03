from django.db import models

from django_oasis import Operation, Resource, model2schema
from django_oasis.pagination import PagePagination
from django_oasis.parameter import Body


# 这是 Django 的 ORM model
class BookModel(models.Model):
    title = models.CharField(max_length=20, verbose_name="书名")
    create_at = models.DateTimeField(auto_now_add=True)


# Oasis 并不能直接理解 Django Model 中的定义，
# 所以需要将 BookModel 转换成 Schema。
BookSchema = model2schema(BookModel)


# 可以先将以下代码理解为 Django 中基于类的视图。
@Resource("/books")
class BookListAPI:
    # get 方法负责处理 GET 请求，用于查询 BookModel
    def get(self, pagination=PagePagination(BookSchema)):
        # 这里使用了 Oasis 提供的分页功能
        return pagination.paginate(BookModel.objects.all())

    # post 方法负责处理 POST 请求，用于新增 BookModel
    @Operation(response_schema=BookSchema)
    def post(self, data=Body(BookSchema)):
        return BookModel.objects.create(**data)
