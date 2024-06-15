from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import JsonData


@Resource("/api")
class API:
    def get(
        self,
        data=JsonData(
            {
                "type": schema.Integer(
                    nullable=True,
                )
            }
        ),
    ): ...
