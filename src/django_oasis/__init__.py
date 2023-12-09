try:
    from .core import OpenAPI, Operation, Resource
    from .model2schema import model2schema
except ImportError:
    pass

from .utils.version import get_version

__version__ = get_version((0, 1, 0, "alpha", 0))
