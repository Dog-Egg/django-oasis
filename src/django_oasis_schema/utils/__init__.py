import importlib
import operator
import typing

from django_oasis import schema

T = typing.TypeVar("T")


def make_instance(obj: typing.Union[T, typing.Type[T]]) -> T:
    if isinstance(obj, type):
        return obj()
    return obj


def import_string(obj_path: str, default_module: str = ""):
    """
    >>> import math
    >>> import_string('math.pi') == math.pi
    True
    """
    if ":" in obj_path:
        module, obj = obj_path.rsplit(":", 1)
    elif "." in obj_path:
        module, obj = obj_path.rsplit(".", 1)
    else:
        module, obj = default_module, obj_path

    return operator.attrgetter(obj)(importlib.import_module(module))


def make_model_schema(obj) -> "schema.Model":
    if isinstance(obj, dict):
        obj = schema.Model.from_dict(obj)
    obj = make_instance(obj)
    if not isinstance(obj, schema.Model):
        raise ValueError("The %r cannot be instantiated as a schemas.Model." % obj)
    return obj


def make_schema(obj) -> "schema.Schema":
    if isinstance(obj, dict):
        return make_model_schema(obj)
    obj = make_instance(obj)
    if not isinstance(obj, schema.Schema):
        raise ValueError("The %r cannot be instantiated as a Schema." % obj)
    return obj
