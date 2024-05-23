import pytest

from . import urls
from .page_pagination import Book


@pytest.mark.urls(urls)
@pytest.mark.django_db
def test_page_pagination(client):
    Book.objects.bulk_create([Book(title="三体", author="老刘")] * 30)

    response = client.get("/books/page")
    assert response.status_code == 200
    assert response.json() == {
        "page": 1,
        "page_size": 20,
        "results": [{"author": "老刘", "id": i, "title": "三体"} for i in range(1, 21)],
        "count": 30,
    }
