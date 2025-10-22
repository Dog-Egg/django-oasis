import zangar as z

import openapi
from openapi.transformation import as_path_item_object


def test_basic():
    class API:
        @openapi.response(200)
        @openapi.response(404)
        @openapi.apply_signature
        def get(
            self,
            request,
            page=openapi.s_query(schema=z.int()),
            page_size=openapi.s_query(schema=z.int()),
        ):
            pass

        @openapi.apply_signature
        def post(
            self,
            request,
            body=openapi.s_body(
                content={
                    "application/json": openapi.MediaType(
                        schema=z.struct({"code": z.int()})
                    )
                }
            ),
        ):
            pass

    assert as_path_item_object(API) == {
        "get": {
            "parameters": [
                {
                    "name": "page",
                    "in": "query",
                    "schema": {"type": "integer"},
                    "required": True,
                },
                {
                    "name": "page_size",
                    "in": "query",
                    "schema": {"type": "integer"},
                    "required": True,
                },
            ],
            "responses": {
                "200": {
                    "description": "OK",
                },
                "400": {
                    "description": "Bad Request",
                },
                "404": {
                    "description": "Not Found",
                },
            },
        },
        "post": {
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "properties": {
                                "code": {
                                    "type": "integer",
                                },
                            },
                            "required": [
                                "code",
                            ],
                            "type": "object",
                        },
                    },
                },
                "required": True,
            },
            "responses": {
                "400": {
                    "description": "Bad Request",
                },
                "415": {
                    "description": "Unsupported Media Type",
                },
            },
        },
    }
