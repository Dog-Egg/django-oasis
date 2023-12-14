import typing as t

import django_oasis_schema as schema

LikeModel = t.Union[
    schema.Model,
    t.Type[schema.Model],
    t.Dict[str, schema.Schema],
]
