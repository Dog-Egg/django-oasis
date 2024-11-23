from django_oasis.core import Resource, schema
from django_oasis.parameter import FormData, FormItem


@Resource("/api1")
class API1:
    def post(
        self,
        form=FormData(
            {
                "a": schema.String(),
                "b": schema.Integer(),
            }
        ),
    ): ...


# 与 API1 声明结果等效
@Resource("/api2")
class API2:
    def post(
        self,
        a=FormItem(schema.String()),
        b=FormItem(schema.Integer()),
    ): ...
