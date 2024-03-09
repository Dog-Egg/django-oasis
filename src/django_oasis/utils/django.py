from django.core.exceptions import ValidationError as DjangoValidationError

from django_oasis import schema


class django_validator_wraps:
    """把 Django 的验证器包装成 Schema 验证器，验证失败将抛出 `ValidationError <django_oasis.schema.ValidationError>` 异常对象。

    .. doctest::

        >>> from django.core.validators import validate_email
        >>> from django_oasis.utils.django import django_validator_wraps

        >>> validate = django_validator_wraps(validate_email)

        >>> validate('123@example.com') # That's right

        >>> validate('example@@')
        Traceback (most recent call last):
            ...
        django_oasis_schema.exceptions.ValidationError: [{'msgs': ['Enter a valid email address.']}]

        >>> repr(validate)
        '<django_validator_wraps: django.core.validators.EmailValidator>'
    """

    def __init__(self, validator) -> None:
        self._wrapped = validator

    def __call__(self, *args, **kwargs):
        try:
            return self._wrapped(*args, **kwargs)
        except DjangoValidationError as exc:
            raise schema.ValidationError(list(exc)[0]) from exc

    def __repr__(self) -> str:
        c = self._wrapped.__class__
        wrapped = c.__module__ + "." + c.__name__
        return f"<django_validator_wraps: {wrapped}>"
