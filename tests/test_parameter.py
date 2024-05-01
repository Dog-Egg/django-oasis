import pytest

from django_oasis import schema
from django_oasis.parameter.parameters import (
    Cookie,
    FormData,
    FormItem,
    JsonData,
    Path,
    Query,
    QueryItem,
    Style,
)


class Color(schema.Model):
    R = schema.Integer()
    G = schema.Integer()
    B = schema.Integer()


def test_query_form_true_string__default(rf):
    assert Query({"color": schema.String()}).parse_request(rf.get("/?color=blue")) == {
        "color": "blue",
    }


def test_query_form_true_array__default(rf):
    assert Query({"color": schema.List(schema.String())}).parse_request(
        rf.get("/?color=blue&color=black&color=brown")
    ) == {"color": ["blue", "black", "brown"]}


def test_query_form_true_object__default(rf):
    assert Query({"color": Color()}).parse_request(rf.get("/?R=100&G=200&B=150")) == {
        "color": {"R": 100, "G": 200, "B": 150}
    }


def test_query_form_false_string(rf):
    assert Query(
        {"color": schema.String()}, styles={"color": Style("form", False)}
    ).parse_request(rf.get("/?color=blue")) == {"color": "blue"}


def test_query_form_false_array(rf):
    assert Query(
        {"color": schema.List(schema.String)},
        styles={"color": Style("form", False)},
    ).parse_request(rf.get("/?color=blue,black,brown")) == {
        "color": ["blue", "black", "brown"]
    }


def test_query_form_false_object(rf):
    assert Query(
        {"color": Color()}, styles={"color": Style("form", False)}
    ).parse_request(rf.get("/?color=R,100,G,200,B,150")) == {
        "color": {"R": 100, "G": 200, "B": 150}
    }


def test_query_spaceDelimited_false_array(rf):
    assert Query(
        {"color": schema.List(schema.String)},
        styles={"color": Style("spaceDelimited", False)},
    ).parse_request(rf.get("/?color=blue%20black%20brown")) == {
        "color": ["blue", "black", "brown"]
    }


def test_query_pipeDelimited_false_array(rf):
    assert Query(
        {"color": schema.List(schema.String)},
        styles={"color": Style("pipeDelimited", False)},
    ).parse_request(rf.get("/?color=blue|black|brown")) == {
        "color": ["blue", "black", "brown"]
    }


def test_query_deepObject_true_object(rf):
    assert Query(
        {"color": Color()}, styles={"color": Style("deepObject", True)}
    ).parse_request(rf.get("/?color[R]=100&color[G]=200&color[B]=150")) == {
        "color": {"R": 100, "G": 200, "B": 150}
    }


def test_QueryItem(rf):
    item = QueryItem(schema.Integer)
    item.setitemname("a")
    assert item.parse_request(rf.get("/?a=1")) == 1


def test_QueryItem2(rf):
    item = QueryItem(schema.String(required=False))
    item.setitemname("a")
    assert item.parse_request(rf.get("/")) is schema.undefined


@pytest.mark.skip("deprecated")
def test_FormItem(rf):
    item = FormItem(schema.Integer)
    item.setitemname("b")
    assert (
        item.parse_request(
            rf.post(
                "/",
                "a=1&b=2",
                content_type="application/x-www-form-urlencoded",
            )
        )
        == 2
    )


def test_cookie_form_false_string__default(rf):
    request = rf.get("/")
    request.COOKIES["color"] = "blue"
    assert Cookie({"color": schema.String()}).parse_request(request) == {
        "color": "blue",
    }


def test_cookie_form_false_array__default(rf):
    req = rf.get("/")
    req.COOKIES["color"] = "blue,red,yellow"
    assert Cookie({"color": schema.List()}).parse_request(req) == {
        "color": ["blue", "red", "yellow"]
    }


def test_cookie_form_false_object__default(rf):
    req = rf.get("/")
    req.COOKIES["color"] = "B,0,G,0,R,0"
    assert Cookie({"color": Color()}).parse_request(req) == {
        "color": {"B": 0, "G": 0, "R": 0}
    }


def test_path_simple_falst_string__default():
    assert Path("/color/{color}").parse_kwargs({"color": "blue"}) == {"color": "blue"}


def test_path_simple_false_array__default():
    assert Path(
        "/color/{color}",
        {"color": schema.List()},
    ).parse_kwargs(
        {"color": "red,blue,yellow"}
    ) == {"color": ["red", "blue", "yellow"]}


def test_path_simple_true_array():
    assert Path(
        "/color/{color}",
        {"color": schema.List()},
        {"color": Style("simple", True)},
    ).parse_kwargs({"color": "red,blue,yellow"}) == {"color": ["red", "blue", "yellow"]}


def test_path_simple_false_object__default():
    assert Path(
        "/color/{color}",
        {"color": Color()},
    ).parse_kwargs(
        {"color": "R,100,G,200,B,150"}
    ) == {"color": {"B": 150, "G": 200, "R": 100}}


def test_path_simple_true_object():
    assert Path(
        "/color/{color}",
        {"color": Color()},
        {"color": Style("simple", True)},
    ).parse_kwargs({"color": "R=100,G=200,B=150"}) == {
        "color": {"B": 150, "G": 200, "R": 100}
    }


def test_FormData_parse_request(rf):
    request = rf.post(
        "/",
        data="a=1&b=1",
        content_type="application/x-www-form-urlencoded",
    )
    result = FormData(
        {
            "a": schema.String(),
            "b": schema.Integer(),
        }
    ).parse_request(request)
    assert result == {"a": "1", "b": 1}


def test_JsonData_parse_request(rf):
    request = rf.post(
        "/",
        data={"a": "1", "b": "2"},
        content_type="application/json",
    )
    result = JsonData({"a": schema.Integer(), "b": schema.String()}).parse_request(
        request
    )
    assert result == {"a": 1, "b": "2"}


def test_upload_file(rf):
    from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

    video = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
    request = rf.post("/", data={"file": video})
    result = FormData({"file": schema.File()}).parse_request(request)
    file = result["file"]
    assert isinstance(file, InMemoryUploadedFile)
    assert file.read() == b"file_content"
    assert file.content_type == "video/mp4"
