import abc
import copy
import typing as t

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.functional import cached_property

from django_oasis import schema
from django_oasis.parameter.parameters import MountPoint, Query, RequestParameter


class Pagination(MountPoint, metaclass=abc.ABCMeta):
    """分页器抽象基类"""

    __reqarg: t.Any

    @cached_property
    def __parameter(self):
        return self._get_request_parameter()

    def __openapispec__(self, oas):
        return self.__parameter.__openapispec__(oas)

    def setup(self, operation):
        if operation.response_schema is None:
            operation.response_schema = self._get_response_schema()

    def parse_request(self, request: HttpRequest):
        this = copy.copy(self)  # TODO copy is not good
        this.__reqarg = self.__parameter.parse_request(request)
        return this

    def paginate(self, queryset: QuerySet):
        """对 Django 查询集进行分页，并返回结果。"""
        return self._get_response(queryset, self.__reqarg)

    @abc.abstractmethod
    def _get_request_parameter(self) -> RequestParameter:
        """定义分页所需要的请求参数，获取的参数结果将传递给 `_get_response`。"""

    @abc.abstractmethod
    def _get_response_schema(self) -> schema.Schema:
        """设置分页响应数据结构，用于设置所在 `Operation <django_oasis.core.Operation>` 的 ``response_schema``。"""

    @abc.abstractmethod
    def _get_response(self, queryset: QuerySet, reqarg):
        """
        获取响应数据。

        :param queryset: 调用 `paginate` 时获取的查询集。
        :param reqarg: 使用 `_get_request_parameter` 返回对象获取到的请求实参。
        """


class PagePagination(Pagination):
    """
    从 URL 参数中获取 ``page`` 和 ``page_size`` 进行分页。

    :param schema: 提供分页列表元素的数据结构。
    """

    def __init__(self, schema: t.Union[schema.Schema, t.Type[schema.Schema]], /):
        super().__init__()
        self.__schema = schema

    def _get_request_parameter(self):
        return Query(
            {
                "page": schema.Integer(default=1, minimum=1),
                "page_size": schema.Integer(default=20, minimum=1),
            }
        )

    def _get_response_schema(self) -> schema.Schema:
        return schema.Model.from_dict(
            {
                "page": schema.Integer(),
                "page_size": schema.Integer(),
                "results": schema.List(self.__schema),
                "count": schema.Integer(),
            }
        )()

    def _get_response(self, queryset: QuerySet, reqarg):
        page, page_size = reqarg["page"], reqarg["page_size"]
        offset = (reqarg["page"] - 1) * reqarg["page_size"]
        return {
            "page": page,
            "page_size": page_size,
            "results": queryset[offset : offset + page_size],
            "count": queryset.count(),
        }


class OffsetPagination(Pagination):
    """
    从 URL 参数中获取 ``offset`` 和 ``limit`` 进行分页。

    :param schema:  提供分页列表元素的数据结构。
    """

    def __init__(self, schema: t.Union[schema.Schema, t.Type[schema.Schema]], /):
        super().__init__()
        self.__schema = schema

    def _get_request_parameter(self):
        return Query(
            {
                "offset": schema.Integer(default=0, minimum=0),
                "limit": schema.Integer(default=20, minimum=1),
            }
        )

    def _get_response_schema(self) -> schema.Schema:
        return schema.Model.from_dict(
            {
                "offset": schema.Integer(),
                "limit": schema.Integer(),
                "results": schema.List(self.__schema),
                "count": schema.Integer(),
            }
        )()

    def _get_response(self, queryset: QuerySet, reqarg):
        offset, limit = reqarg["offset"], reqarg["limit"]
        return {
            "offset": offset,
            "limit": limit,
            "results": queryset[offset : offset + limit],
            "count": queryset.count(),
        }
