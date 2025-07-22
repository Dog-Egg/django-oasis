import zangar as z
from django.test import RequestFactory

import openapi


class TestSignatureParameters:
    def test_py_default(self):
        @openapi.apply_signature
        def func(_, request, a=openapi.s_query(schema=z.to.int(), py_default=123)):
            return a

        rf = RequestFactory()
        assert func(None, rf.get("/?a=1")) == 1
        assert func(None, rf.get("/")) == 123
