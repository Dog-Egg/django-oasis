from django_oasis import Operation, Resource
from django_oasis.auth import BaseAuth
from django_oasis.exceptions import UnauthorizedError


class IsOurUser(BaseAuth):
    def check_auth(self, request):
        # 若用户未登录，抛出 UnauthorizedError，这将返回 HTTP 401 响应。
        if not request.user.is_authenticated:
            raise UnauthorizedError

    def __openapispec__(self, spec, **kwargs):
        spec.set_security_scheme(
            "fooName",
            {
                "type": "http",
                "scheme": "basic",
            },
        )
        return [{"fooName": []}]


@Resource("/to/path")
class API:
    @Operation(auth=IsOurUser)
    def get(self):
        ...
