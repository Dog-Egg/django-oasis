import json


def test_paging(rf):
    from samples.paging import FooAPI

    view = FooAPI.as_view()

    # default paging
    response = view(rf.get("/"))
    assert json.loads(response.content) == {
        "items": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        "current_page_size": 10,
        "current_size": 1,
        "total": 14,
    }

    # custom page
    response = view(rf.get("/?page=2"))
    assert json.loads(response.content) == {
        "current_page_size": 10,
        "current_size": 2,
        "items": ["k", "l", "m", "n"],
        "total": 14,
    }
