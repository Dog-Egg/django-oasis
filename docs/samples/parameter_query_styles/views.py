from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import QueryItem, Style


@Resource("/array/form/true")
class ArrayFormTrueAPI:
    def get(
        self,
        color=QueryItem(
            schema.List(schema.String()),
            Style("form", True),
        ),
    ):
        ...
        return color


@Resource("/array/form/false")
class ArrayFormFalseAPI:
    def get(
        self,
        color=QueryItem(
            schema.List(schema.String()),
            Style("form", False),
        ),
    ):
        ...
        return color


@Resource("/array/spaceDelimited/false")
class ArraySpaceDelimitedFalseAPI:
    def get(
        self,
        color=QueryItem(
            schema.List(schema.String()),
            Style("spaceDelimited", False),
        ),
    ):
        ...
        return color


@Resource("/array/pipeDelimited/false")
class ArrayPipeDelimitedFalseAPI:
    def get(
        self,
        color=QueryItem(
            schema.List(schema.String()),
            Style("pipeDelimited", False),
        ),
    ):
        ...
        return color


@Resource("/object/form/true")
class ObjectFormTrueAPI:
    def get(
        self,
        color=QueryItem(
            schema.Model.from_dict(
                {
                    "R": schema.Integer(),
                    "G": schema.Integer(),
                    "B": schema.Integer(),
                }
            ),
            Style("form", True),
        ),
    ):
        ...
        return color


@Resource("/object/form/false")
class ObjectFormFalseAPI:
    def get(
        self,
        color=QueryItem(
            schema.Model.from_dict(
                {
                    "R": schema.Integer(),
                    "G": schema.Integer(),
                    "B": schema.Integer(),
                }
            ),
            Style("form", False),
        ),
    ):
        ...
        return color


@Resource("/object/deepObject/true")
class ObjectDeepObjectTrueAPI:
    def get(
        self,
        color=QueryItem(
            schema.Model.from_dict(
                {
                    "R": schema.Integer(),
                    "G": schema.Integer(),
                    "B": schema.Integer(),
                }
            ),
            Style("deepObject", True),
        ),
    ):
        ...
        return color
