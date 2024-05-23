import pytest

from . import urls


@pytest.mark.django_db
@pytest.mark.urls(urls)
def test(client, django_user_model, admin_client):
    resp = client.post("/to/path")
    assert resp.status_code == 401
    assert resp.json() == {"reason": "Unauthorized", "status_code": 401}

    user = django_user_model.objects.create(
        username="someone", password="something"
    )  # 普通用户
    client.force_login(user)
    resp = client.post("/to/path")
    assert resp.status_code == 403
    assert resp.json() == {"reason": "Forbidden", "status_code": 403}

    resp = admin_client.post("/to/path")
    assert resp.status_code == 200
