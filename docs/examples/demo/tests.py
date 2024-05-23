import pytest

from django_oasis.urls import reverse

from . import urls, views


@pytest.mark.urls(urls)
@pytest.mark.django_db
def test(client):
    response = client.get(reverse(views.BookListAPI))
    assert response.status_code == 200
