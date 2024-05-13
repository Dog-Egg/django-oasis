import warnings as _warnings

from .utils.version import get_version as _get_version

__version__ = _get_version((0, 1, 0, "alpha", 0))


def __getattr__(name):
    if name == "OpenAPI":
        from .core import OpenAPI

        _warnings.warn(
            'Use "from django_oasis.core import OpenAPI" instead of "from django_oasis import OpenAPI".',
            DeprecationWarning,
            stacklevel=2,
        )
        return OpenAPI
    elif name == "Operation":
        from .core import Operation

        _warnings.warn(
            'Use "from django_oasis.core import Operation" instead of "from django_oasis import Operation".',
            DeprecationWarning,
            stacklevel=2,
        )
        return Operation
    elif name == "Resource":
        from .core import Resource

        _warnings.warn(
            'Use "from django_oasis.core import Resource" instead of "from django_oasis import Resource".',
            DeprecationWarning,
            stacklevel=2,
        )
        return Resource
    elif name == "model2schema":
        from .common import model2schema

        _warnings.warn(
            'Use "from django_oasis.common import model2schema" instead of "from django_oasis import model2schema".',
            DeprecationWarning,
            stacklevel=2,
        )
        return model2schema
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
