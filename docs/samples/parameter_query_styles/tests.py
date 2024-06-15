import pytest

from django_oasis.urls import reverse

from . import urls, views

array_expected = ["blue", "black", "brown"]


@pytest.mark.urls(urls)
def test_ArrayFormTrueAPI(client):
    response = client.get(
        reverse(views.ArrayFormTrueAPI) + "?color=blue&color=black&color=brown"
    )
    assert response.json() == array_expected


@pytest.mark.urls(urls)
def test_ArrayFormFalseAPI(client):
    response = client.get(reverse(views.ArrayFormFalseAPI) + "?color=blue,black,brown")
    assert response.json() == array_expected


@pytest.mark.urls(urls)
def test_ArraySpaceDelimitedFalseAPI(client):
    response = client.get(
        reverse(views.ArraySpaceDelimitedFalseAPI) + "?color=blue black brown"
    )
    assert response.json() == array_expected


@pytest.mark.urls(urls)
def test_ArrayPipeDelimitedFalseAPI(client):
    response = client.get(
        reverse(views.ArrayPipeDelimitedFalseAPI) + "?color=blue|black|brown"
    )
    assert response.json() == array_expected


object_expected = {"R": 100, "G": 200, "B": 150}


@pytest.mark.urls(urls)
def test_ObjectFormTrueAPI(client):
    response = client.get(reverse(views.ObjectFormTrueAPI) + "?R=100&G=200&B=150")
    assert response.json() == object_expected


@pytest.mark.urls(urls)
def test_ObjectFormFalseAPI(client):
    response = client.get(
        reverse(views.ObjectFormFalseAPI) + "?color=R,100,G,200,B,150"
    )
    assert response.json() == object_expected


@pytest.mark.urls(urls)
def test_ObjectDeepObjectTrueAPI(client):
    response = client.get(
        reverse(views.ObjectDeepObjectTrueAPI)
        + "?color[R]=100&color[G]=200&color[B]=150"
    )
    assert response.json() == object_expected
