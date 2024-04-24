import pytest


def test_response_serialize_error_message(client):
    with pytest.raises(
        ValueError,
        match="{'a': 'a'} cannot be serialized by {'a': <django_oasis_schema.schemas.Integer object at .*?>}.",
    ):
        client.get("/1")
