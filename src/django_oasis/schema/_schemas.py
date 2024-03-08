from django.conf import settings
from django.core.validators import URLValidator

import django_oasis_schema as schema
from django_oasis.utils.django import django_validator_wraps

__all__ = (
    "Path",
    "File",
    "Url",
    "Datetime",
)


class Path(schema.String):
    pass


class File(schema.Schema):
    class Meta:
        data_type = "string"
        data_format = "binary"

    def _serialize(self, obj):
        raise NotImplementedError


class Datetime(schema.Datetime):
    def __init__(self, **kwargs):
        kwargs.setdefault("with_tz", settings.USE_TZ)
        super().__init__(**kwargs)


class Url(schema.String):
    @schema.as_validator
    def _validate_url(self, value):
        django_validator_wraps(URLValidator())(value)
