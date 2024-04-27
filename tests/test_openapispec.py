from django_oasis import Operation, Resource, schema
from django_oasis.auth import BaseAuth
from django_oasis_schema.spectools.objects import OpenAPISpec


def test_securitySchemes():

    class MyAuth(BaseAuth):
        def __openapispec__(self, spec, **kwargs):
            spec.set_security_scheme(
                "myauth",
                {
                    "type": "oauth2",
                    "flows": {
                        "implicit": {
                            "authorizationUrl": "https://example.com/dialog",
                            "scopes": {},
                        }
                    },
                },
            )
            return [{"myauth": []}]

    spec = OpenAPISpec(info={})
    spec.parse(Operation(auth=MyAuth))
    assert spec.to_dict()["components"]["securitySchemes"] == {
        "myauth": {
            "type": "oauth2",
            "flows": {
                "implicit": {
                    "authorizationUrl": "https://example.com/dialog",
                    "scopes": {},
                }
            },
        }
    }


def test_reference_object():
    class FooSchema(schema.Model):
        name = schema.String()

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
                    "tests.test_openapispec.test_reference_object.<locals>.FooSchema": {
                        "title": "FooSchema",
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
                                                "$ref": "#/components/schemas/tests.test_openapispec.test_reference_object.<locals>.FooSchema",
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
                                                    "$ref": "#/components/schemas/tests.test_openapispec.test_reference_object.<locals>.FooSchema",
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
