from django_oasis import schema


class BookSchema(schema.Model):
    title = schema.String()
    author = schema.String(required=False)
    classification = schema.Integer(default="传记")
