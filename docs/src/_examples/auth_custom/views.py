from django_oasis.auth import BaseAuth
from django_oasis.core import Operation, Resource
from django_oasis.exceptions import UnauthorizedError


class IsOurUser(BaseAuth):

    declare_security = {
        "type": "http",
        "scheme": "basic",
    }

    declare_responses = {
        401: {
            "description": "未登录",
        }
    }

    def check_auth(self, request):
        # 若用户未登录，抛出 UnauthorizedError，这将返回 HTTP 401 响应。
        if not request.user.is_authenticated:
            raise UnauthorizedError


@Resource("/to/path")
class API:
    @Operation(auth=IsOurUser)
    def get(self): ...
