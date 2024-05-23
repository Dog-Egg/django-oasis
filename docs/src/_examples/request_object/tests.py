import pytest

from django_oasis.urls import reverse

from . import urls, views


@pytest.mark.urls(urls)
def test(admin_client):
    response = admin_client.get(reverse(views.API))
    assert response.content == b"Hello admin"
