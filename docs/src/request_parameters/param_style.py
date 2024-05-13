from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import Query, Style


@Resource("/to/path")
class API:
    def get(
        self,
        query=Query(
            {
                "a": schema.List(),
                "b": schema.List(),
            },
            styles={
                # "a": Style("form", True), # 默认样式
                "b": Style("form", False),
            },
        ),
    ): ...
