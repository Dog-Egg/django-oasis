from django.db import models

from django_oasis import schema
from django_oasis.common import model2schema
from django_oasis.core import Resource
from django_oasis.pagination import Pagination
from django_oasis.parameter import Query


class Book(models.Model):
    title = models.CharField(max_length=10, verbose_name="书名")
    author = models.CharField(max_length=20, verbose_name="作者")


class BookSchema(model2schema(Book)):
    pass


class MyPagination(Pagination):
    def __init__(self, item_schema):
        # 初始化时，需要提供分页项目的schema
        self._item_schema = item_schema

    def _get_request_parameter(self):
        # 该方法是告诉分页器从哪里获取请求参数。
        # 获取到的参数会传给 `_get_response`。
        return Query(
            {
                "page": schema.Integer(
                    default=1, minimum=1, alias="p", description="页码"
                ),
                "page_size": schema.Integer(
                    default=20, minimum=1, alias="size", description="页面大小"
                ),
            }
        )

    def _get_response_schema(self):
        # 该方法为所在 Operation 设置 response_schema

        class ResponseSchema(schema.Model):
            data = schema.List(self._item_schema, description="数据列表")
            total = schema.Integer(description="数据总数")

        return ResponseSchema()

    def _get_response(self, queryset, reqarg):
        # 返回请求响应。
        page, page_size = reqarg["page"], reqarg["page_size"]
        offset = (page - 1) * page_size

        # 无需手动序列化，因为已经实现了 `_get_response_schema` 方法。
        return {
            "items": queryset[offset : offset + page_size],
            "total": queryset.count(),
        }


@Resource("/books")
class BookListAPI:
    def get(self, pagination=MyPagination(BookSchema)):
        return pagination.paginate(Book.objects.all())
