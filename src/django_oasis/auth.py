import abc

from django.conf import settings
from django.http import HttpRequest

from django_oasis import exceptions
from django_oasis_schema.spectools.objects import OpenAPISpec


class BaseAuth:
    """
    认证基类。如需自定义认证类，需继承该类，并实现其抽象方法。
    """

    @abc.abstractmethod
    def check_auth(self, request):
        """
        需自行实现该方法，用于判断请求认证是否成功。如果认证失败，需要抛出异常来停止请求的继续处理。

        :param request: Django `HttpRequest <https://docs.djangoproject.com/zh-hans/5.0/ref/request-response/#httprequest-objects>`_ 对象。
        """

    @abc.abstractmethod
    def __openapispec__(self, spec, **kwargs):
        """
        需自行实现该方法，该方法为 OpenAPISpec 对象能识别的方法。

        需要通过 ``spec.set_security_scheme`` 方法为 OAS `securitySchemes <https://spec.openapis.org/oas/v3.0.3#componentsSecuritySchemes>`_ 字段设置值。

        并且返回值将用于设置 OAS `Operation security <https://spec.openapis.org/oas/v3.0.3#operationSecurity>`_ 字段。
        """


class DjangoAuthBase(BaseAuth):
    def _check_user(self, request):
        raise NotImplementedError

    def check_auth(self, request):
        if not self._check_user(request):
            if request.user.is_authenticated:
                raise exceptions.ForbiddenError
            raise exceptions.UnauthorizedError

    def __openapispec__(self, spec: OpenAPISpec, **kwargs):
        key = "__auth__"
        spec.set_security_scheme(
            key,
            {
                "type": "apiKey",
                "name": settings.SESSION_COOKIE_NAME,
                "in": "cookie",
            },
        )
        return [{key: []}]


class IsAuthenticated(DjangoAuthBase):
    """验证用户是否登录。"""

    def _check_user(self, request: HttpRequest):
        return request.user.is_authenticated


class IsSuperuser(DjangoAuthBase):
    """验证用户是否为超级管理员。"""

    def _check_user(self, request: HttpRequest):
        return request.user.is_superuser  # type: ignore


class IsAdministrator(DjangoAuthBase):
    """验证用户是否为管理员。"""

    def _check_user(self, request: HttpRequest):
        return request.user.is_staff  # type: ignore


class HasPermission(DjangoAuthBase):
    """
    验证用户是否拥有某权限。内部调用 `has_perm <https://docs.djangoproject.com/zh-hans/5.0/ref/contrib/auth/#django.contrib.auth.models.User.has_perm>`_ 方法。

    :param perm: 描述权限的字符串，格式是 "<app label>.<permission codename>"。
    """

    def __init__(self, perm: str):
        self.__perm = perm

    def _check_user(self, request: HttpRequest):
        return request.user.has_perm(self.__perm)  # type: ignore
