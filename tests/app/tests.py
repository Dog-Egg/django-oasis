import pytest
from django.test import override_settings

from django_oasis.urls import reverse

from . import views


def test_response_serialize_error_message(client):
    with pytest.raises(
        ValueError,
        match="{'a': 'a'} cannot be serialized by {'a': <django_oasis_schema.schemas.Integer object at .*?>}.",
    ):
        client.get(reverse(views.API))


@override_settings(ROOT_URLCONF="tests.app.urls2")
def test_swagger_ui(client):
    from django_oasis.docs import _get_swagger_ui_urls

    assert _get_swagger_ui_urls() == [
        {"name": "API Document", "url": "/sub/api/apispec_e08ac8fc"}
    ]

    response = client.get("/apidocs/")
    assert response.status_code == 200
