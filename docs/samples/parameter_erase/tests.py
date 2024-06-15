import pytest

from django_oasis.urls import reverse

from . import urls, views


@pytest.mark.urls(urls)
def test(client):
    response = client.get(reverse(views.API) + "?a=&b=1")
    assert response.json() == {"b": "1"}
