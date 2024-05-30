from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import Style


@Resource(
    "/array/simple/false/{color}",
    param_schemas={
        "color": schema.List(schema.String()),
    },
    param_styles={
        "color": Style("simple", False),  # 默认样式
    },
)
class ArraySimpleFalseAPI:
    def __init__(self, request, colors):
        self.colors = colors

    def get(self):
        ...
        return self.colors


@Resource(
    "/object/simple/false/{color}",
    param_schemas={
        "color": schema.Model.from_dict(
            {
                "R": schema.Integer(),
                "G": schema.Integer(),
                "B": schema.Integer(),
            }
        )()
    },
    param_styles={
        "color": Style("simple", False),  # 默认样式
    },
)
class ObjectSimpleFalseAPI:
    def __init__(self, request, color):
        self.color = color

    def get(self):
        ...
        return self.color


@Resource(
    "/object/simple/true/{color}",
    param_schemas={
        "color": schema.Model.from_dict(
            {
                "R": schema.Integer(),
                "G": schema.Integer(),
                "B": schema.Integer(),
            }
        )()
    },
    param_styles={
        "color": Style("simple", True),
    },
)
class ObjectSimpleTrueAPI:
    def __init__(self, request, color):
        self.color = color

    def get(self):
        ...
        return self.color
