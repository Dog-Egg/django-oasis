from django.urls import reverse as _reverse
from django.utils.functional import lazy

from django_oasis.core import Resource

__all__ = ("reverse", "reverse_lazy")


def reverse(viewname, *args, **kwargs):
    resource = Resource.checkout(viewname)
    if resource is not None:
        viewname = resource.view_func
    return _reverse(viewname, *args, **kwargs)


reverse_lazy = lazy(reverse, str)
