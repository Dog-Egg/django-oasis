from django_oasis.auth import BaseAuth
from django_oasis.core import OpenAPI, Operation, Resource, schema
from django_oasis_schema.spectools.objects import OpenAPISpec


def test_auth_openapispec():

    class MyAuth(BaseAuth):
        declare_responses = {
            401: {
                "description": "未登录",
            }
        }

        declare_security = {
            "type": "oauth2",
            "flows": {
                "implicit": {
                    "authorizationUrl": "https://example.com/dialog",
                    "scopes": {},
                }
            },
        }

    @Resource("/")
    class API:
        @Operation(auth=MyAuth)
        def get(self): ...

    openapi = OpenAPI()
    openapi.add_resource(API)

    spec = openapi.get_spec()

    assert spec["components"]["securitySchemes"] == {
        "MyAuth": {
            "type": "oauth2",
            "flows": {
                "implicit": {
                    "authorizationUrl": "https://example.com/dialog",
                    "scopes": {},
                }
            },
        }
    }
    assert spec["paths"]["/"]["get"] == {
        "responses": {
            200: {
                "description": "OK",
            },
            401: {
                "description": "未登录",
            },
        },
        "security": [
            {
                "MyAuth": [],
            },
        ],
    }


class FooSchema(schema.Model):
    """__doc__ description"""

    name = schema.String()


def test_reference_object():

    @Resource("/")
    class API:
        @Operation(response_schema=schema.List(FooSchema(required_fields=[])))
        def get(self): ...

        @Operation(response_schema=FooSchema(description="描述", nullable=True))
        def post(self): ...

    spec = OpenAPISpec(info={})
    spec.add_path("/", spec.parse(Resource.checkout(API)))

    # 调用多次的结果应保持一致
    for _ in range(5):
        assert spec.to_dict() == {
            "components": {
                "schemas": {
                    "tests.test_openapispec.FooSchema": {
                        "title": "FooSchema",
                        "description": "__doc__ description",
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                            }
                        },
                    },
                },
            },
            "openapi": "3.0.3",
            "paths": {
                "/": {
                    "get": {
                        "responses": {
                            200: {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "items": {
                                                "$ref": "#/components/schemas/tests.test_openapispec.FooSchema",
                                            },
                                            "type": "array",
                                        },
                                    },
                                },
                                "description": "OK",
                            },
                        },
                    },
                    "post": {
                        "responses": {
                            200: {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "description": "描述",
                                            "nullable": True,
                                            "allOf": [
                                                {
                                                    "$ref": "#/components/schemas/tests.test_openapispec.FooSchema",
                                                },
                                                {
                                                    "required": ["name"],
                                                },
                                            ],
                                        },
                                    },
                                },
                                "description": "OK",
                            },
                        },
                    },
                },
            },
        }


def test_openapi_func_description(rf):
    import json

    openapi = OpenAPI(description=lambda request: "description")
    assert json.loads(openapi.spec_view(rf.get("/")).content) == {
        "openapi": "3.0.3",
        "info": {
            "title": "API Document",
            "version": "0.1.0",
            "description": "description",
        },
    }
