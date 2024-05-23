import pytest

from . import urls
from .models import Book


@pytest.mark.urls(urls)
@pytest.mark.django_db
def test(client):
    # 增
    response = client.post(
        "/books",
        data={"title": "三体", "author": "刘慈欣"},
        content_type="application/json",
    )
    assert response.status_code == 201
    assert response.json() == {"author": "刘慈欣", "id": 1, "title": "三体"}

    # 分页查
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == {
        "count": 1,
        "page": 1,
        "page_size": 20,
        "results": [{"author": "刘慈欣", "id": 1, "title": "三体"}],
    }

    # id 查
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json() == {"author": "刘慈欣", "id": 1, "title": "三体"}

    # 404
    response = client.get("/books/999")
    assert response.status_code == 404

    # 改
    response = client.put(
        "/books/1", {"author": "老刘"}, content_type="application/json"
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_errors": [{"loc": ["title"], "msgs": ["This field is required."]}]
    }

    response = client.put(
        "/books/1", {"title": "三体", "author": "老刘"}, content_type="application/json"
    )
    assert response.json() == {"author": "老刘", "id": 1, "title": "三体"}

    response = client.patch(
        "/books/1", {"title": "小说"}, content_type="application/json"
    )
    assert response.json() == {"author": "老刘", "id": 1, "title": "小说"}

    # 删
    response = client.delete("/books/1")
    assert response.status_code == 204
    assert Book.objects.filter(id=1).first() is None
