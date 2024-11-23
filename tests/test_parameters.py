import pytest

from django_oasis import schema
from django_oasis.exceptions import (
    BadRequestError,
    RequestValidationError,
    UnsupportedMediaTypeError,
)
from django_oasis.parameter import Style
from django_oasis.parameter.parameters import (
    AssemblyWorker,
    Cookie,
    FormData,
    FormItem,
    Header,
    JsonData,
    MountPointSet,
    MountPointSetWrapper,
    Path,
    Query,
    QueryItem,
)


@pytest.fixture
def oas():
    from build_openapispec import openapispec

    return openapispec("3.0.3")


class TestParameterStyles:
    class Color(schema.Model):
        R = schema.Integer()
        G = schema.Integer()
        B = schema.Integer()

    def test_query_form_true_string__default(self, rf):
        assert Query({"color": schema.String()}).parse_request(
            rf.get("/?color=blue")
        ) == {
            "color": "blue",
        }

    def test_query_form_true_array__default(self, rf):
        assert Query({"color": schema.List(schema.String())}).parse_request(
            rf.get("/?color=blue&color=black&color=brown")
        ) == {"color": ["blue", "black", "brown"]}

    def test_query_form_true_object__default(self, rf):
        assert Query({"color": self.Color()}).parse_request(
            rf.get("/?R=100&G=200&B=150")
        ) == {"color": {"R": 100, "G": 200, "B": 150}}

    def test_query_form_false_string(self, rf):
        assert Query(
            {"color": schema.String()}, styles={"color": Style("form", False)}
        ).parse_request(rf.get("/?color=blue")) == {"color": "blue"}

    def test_query_form_false_array(self, rf):
        assert Query(
            {"color": schema.List(schema.String)},
            styles={"color": Style("form", False)},
        ).parse_request(rf.get("/?color=blue,black,brown")) == {
            "color": ["blue", "black", "brown"]
        }

    def test_query_form_false_object(self, rf):
        assert Query(
            {"color": self.Color()}, styles={"color": Style("form", False)}
        ).parse_request(rf.get("/?color=R,100,G,200,B,150")) == {
            "color": {"R": 100, "G": 200, "B": 150}
        }

    def test_query_spaceDelimited_false_array(self, rf):
        assert Query(
            {"color": schema.List(schema.String)},
            styles={"color": Style("spaceDelimited", False)},
        ).parse_request(rf.get("/?color=blue%20black%20brown")) == {
            "color": ["blue", "black", "brown"]
        }

    def test_query_pipeDelimited_false_array(self, rf):
        assert Query(
            {"color": schema.List(schema.String)},
            styles={"color": Style("pipeDelimited", False)},
        ).parse_request(rf.get("/?color=blue|black|brown")) == {
            "color": ["blue", "black", "brown"]
        }

    def test_query_deepObject_true_object(self, rf):
        assert Query(
            {"color": self.Color()}, styles={"color": Style("deepObject", True)}
        ).parse_request(rf.get("/?color[R]=100&color[G]=200&color[B]=150")) == {
            "color": {"R": 100, "G": 200, "B": 150}
        }

    def test_cookie_form_false_string__default(self, rf):
        request = rf.get("/")
        request.COOKIES["color"] = "blue"
        assert Cookie({"color": schema.String()}).parse_request(request) == {
            "color": "blue",
        }

    def test_cookie_form_false_array__default(self, rf):
        req = rf.get("/")
        req.COOKIES["color"] = "blue,red,yellow"
        assert Cookie({"color": schema.List()}).parse_request(req) == {
            "color": ["blue", "red", "yellow"]
        }

    def test_cookie_form_false_object__default(self, rf):
        req = rf.get("/")
        req.COOKIES["color"] = "B,0,G,0,R,0"
        assert Cookie({"color": self.Color()}).parse_request(req) == {
            "color": {"B": 0, "G": 0, "R": 0}
        }

    def test_header_simple_false_primitive__default(self, rf):
        assert Header({"color": schema.String()}).parse_request(
            rf.get("/", headers={"color": "blue"})
        ) == {"color": "blue"}

    def test_header_simple_false_array(self, rf):
        assert Header.default_style == Style("simple", False)
        assert Header({"color": schema.List()}).parse_request(
            rf.get("/", headers={"color": "blue,red,yellow"})
        ) == {"color": ["blue", "red", "yellow"]}

    def test_path_simple_falst_string__default(self):
        assert Path("/color/{color}").parse_kwargs({"color": "blue"}) == {
            "color": "blue"
        }

    def test_path_simple_false_array__default(self):
        assert Path(
            "/color/{color}",
            {"color": schema.List()},
        ).parse_kwargs(
            {"color": "red,blue,yellow"}
        ) == {"color": ["red", "blue", "yellow"]}

    def test_path_simple_true_array(self):
        assert Path(
            "/color/{color}",
            {"color": schema.List()},
            {"color": Style("simple", True)},
        ).parse_kwargs({"color": "red,blue,yellow"}) == {
            "color": ["red", "blue", "yellow"]
        }

    def test_path_simple_false_object__default(self):
        assert Path(
            "/color/{color}",
            {"color": self.Color()},
        ).parse_kwargs(
            {"color": "R,100,G,200,B,150"}
        ) == {"color": {"B": 150, "G": 200, "R": 100}}

    def test_path_simple_true_object(self):
        assert Path(
            "/color/{color}",
            {"color": self.Color()},
            {"color": Style("simple", True)},
        ).parse_kwargs({"color": "R=100,G=200,B=150"}) == {
            "color": {"B": 150, "G": 200, "R": 100}
        }


class TestBodyParameters:
    def test_FormData(self, rf):
        assert FormData({"a": schema.String(), "b": schema.Integer()}).parse_request(
            rf.post(
                "/",
                data="a=1&b=1",
                content_type="application/x-www-form-urlencoded",
            )
        ) == {"a": "1", "b": 1}


def test_RequestValidationError(rf):
    with pytest.raises(RequestValidationError) as e:
        Query({"a": schema.String()}).parse_request(rf.get("/"))
    assert e.value.location == "query"
    assert e.value.exc.format_errors() == [
        {
            "loc": [
                "a",
            ],
            "msgs": [
                "This field is required.",
            ],
        },
    ]

    with pytest.raises(RequestValidationError) as e:
        FormData({"b": schema.String()}).parse_request(
            rf.post("/", content_type="application/x-www-form-urlencoded")
        )
    assert e.value.location == "body"
    assert e.value.exc.format_errors() == [
        {
            "loc": [
                "b",
            ],
            "msgs": [
                "This field is required.",
            ],
        },
    ]


def test_UnsupportedMediaTypeError(rf):
    with pytest.raises(UnsupportedMediaTypeError):
        JsonData({"a": schema.String()}).parse_request(rf.post("/"))


def test_invalid_json_data(rf):
    with pytest.raises(BadRequestError, match="Invalid JSON data"):
        MountPointSet({"a": JsonData(schema.String())}).parse_request(
            rf.post("/", data="None", content_type="application/json")
        )


class TestComponentItem:
    def test(self, rf):
        worker = AssemblyWorker(
            {
                "q1": QueryItem(schema.String()),
                "q2": QueryItem(schema.String(attr="qq2")),  # attr 不影响结果
                "q3": QueryItem(schema.String(required=False)),
            }
        )
        mps = MountPointSet(dict(worker.request_parameters))
        assert worker.split(mps.parse_request(rf.get("/?q1=1&q2=1"))) == {
            "q1": "1",
            "q2": "1",
            "q3": schema.undefined,
        }


def test_upload_file(rf):
    from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

    video = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
    request = rf.post("/", data={"file": video})
    result = FormData({"file": schema.File()}).parse_request(request)
    file = result["file"]
    assert isinstance(file, InMemoryUploadedFile)
    assert file.read() == b"file_content"
    assert file.content_type == "video/mp4"


def test_check_mountpoints():
    with pytest.raises(
        RuntimeError, match="FormItem and JsonData cannot be used together"
    ):
        MountPointSetWrapper(
            {"a": FormItem(schema.String()), "b": JsonData(schema.String())}
        )

    with pytest.raises(RuntimeError, match="JsonData cannot be used more than once"):
        MountPointSetWrapper(
            {"a": JsonData(schema.String()), "b": JsonData(schema.String())}
        )
