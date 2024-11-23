from django_oasis.core import Resource, schema
from django_oasis.parameter import JsonData, JsonItem


@Resource("/api1")
class API1:
    def post(
        self,
        data=JsonData(
            {
                "a": schema.Integer(),
                "b": schema.String(),
            }
        ),
    ): ...


# 与 API1 声明结果等效
@Resource("/api2")
class API2:
    def post(
        self,
        a=JsonItem(schema.Integer()),
        b=JsonItem(schema.String()),
    ): ...
