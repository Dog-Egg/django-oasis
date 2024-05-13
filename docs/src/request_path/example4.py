from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import Style


@Resource(
    "/color/{colors}",
    param_schemas={
        "colors": schema.List(schema.String(choices=["blue", "red", "yellow"]))
    },
    param_styles={"colors": Style("simple", False)},  # 这是默认样式
)
class API:
    def __init__(self, request, colors): ...

    def get(self): ...
