import abc
import typing as t

from django.conf import settings
from django.http import HttpRequest

from django_oasis import exceptions


class BaseAuth:
    """
    认证基类。如需自定义认证类，需继承该类，并实现其抽象方法。
    """

    #: 描述认证时会产生的响应。键为 HTTP 状态码，值为 `Response Object <https://spec.openapis.org/oas/v3.0.3.html#response-object>`_。
    declare_responses: t.Dict[int, dict]

    #: 定义认证使用的安全方案。declare_security 的值为 `Security Scheme Object <https://spec.openapis.org/oas/v3.0.3.html#security-scheme-object>`_。
    declare_security: dict

    @abc.abstractmethod
    def check_auth(self, request):
        """
        需自行实现该方法，用于判断请求认证是否成功。如果认证失败，需要抛出异常来停止请求的继续处理。

        :param request: Django `HttpRequest <https://docs.djangoproject.com/zh-hans/5.0/ref/request-response/#httprequest-objects>`_ 对象。
        """

    def __openapispec__(self, spec, **kwargs):
        if hasattr(self, "declare_security"):
            security_name = self.__class__.__name__
            spec._set_security_scheme(security_name, self.declare_security)
            return [{security_name: []}]


def _get_django_auth_secrity_apikey_name():
    from django.conf.global_settings import SESSION_COOKIE_NAME
    from django.core.exceptions import ImproperlyConfigured

    try:
        return settings.SESSION_COOKIE_NAME
    except ImproperlyConfigured:
        return SESSION_COOKIE_NAME


class DjangoAuthBase(BaseAuth):

    declare_security = {
        "type": "apiKey",
        "name": _get_django_auth_secrity_apikey_name(),
        "in": "cookie",
    }

    def _check_user(self, request):
        raise NotImplementedError

    def check_auth(self, request):
        if not self._check_user(request):
            if request.user.is_authenticated:
                raise exceptions.ForbiddenError
            raise exceptions.UnauthorizedError


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
