from django_oasis import Operation
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
