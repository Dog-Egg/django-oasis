import pytest

from django_oasis.urls import reverse

from . import urls, views

array_expected = ["blue", "black", "brown"]


@pytest.mark.urls(urls)
def test_ArraySimpleFalseAPI(client):
    response = client.get(
        reverse(views.ArraySimpleFalseAPI), headers={"color": "blue,black,brown"}
    )
    assert response.json() == array_expected
