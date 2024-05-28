import pytest

from django_oasis.urls import reverse

from . import urls, views

array_expected = ["blue", "black", "brown"]


@pytest.mark.urls(urls)
def test_ArrayFormFalseAPI(client):
    client.cookies["color"] = "blue,black,brown"
    response = client.get(reverse(views.ArrayFormFalseAPI))
    assert response.json() == array_expected
