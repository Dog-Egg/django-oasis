from django_oasis import schema


class Model(schema.Model):
    a = schema.Integer(attr="attr", alias="alias")
