from django_oasis import schema
from django_oasis.core import Operation, Resource
from django_oasis.parameter import JsonData


class MyModel(schema.Model):
    a = schema.String(read_only=True)  # 字段 a 设置为 “只读”
    b = schema.String(write_only=True)  # 字段 b 设置为 “只写”


@Resource("/api")
class API:
    @Operation(response_schema=MyModel)
    def post(
        self,
        data=JsonData(MyModel),
    ): ...
