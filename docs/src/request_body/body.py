from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import Body


class BookSchema(schema.Model):
    title = schema.String(description="书名")
    created_at = schema.Datetime(description="创建时间")


@Resource("/to/path")
class API:
    def post(self, body=Body(BookSchema)): ...
