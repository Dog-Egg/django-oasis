from dataclasses import dataclass
from datetime import datetime

from django_oasis import schema
from django_oasis.core import Operation, Resource


# 这里用 dataclass 来模拟创建对象
@dataclass
class Book:
    title: str
    created_at: datetime


class BookSchema(schema.Model):
    title = schema.String()
    created_at = schema.Datetime()


@Resource("/api")
class API:
    @Operation(
        response_schema=BookSchema,
    )
    def get(self):
        return Book(
            title="The Book",
            created_at=datetime.now(),
        )
