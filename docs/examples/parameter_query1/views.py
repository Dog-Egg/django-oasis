from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import Query


# 定义所需的参数结构
# 这里定义了 2 个参数 a, b
class QuerySchema(schema.Model):
    a = schema.String()
    b = schema.Integer()


@Resource("/to/path")
class API:
    def get(
        self,
        query=Query(QuerySchema),  # 以关键字参数的形式设置在请求操作函数中
    ): ...
