import pytest


def test_deprecated_import():
    from django_oasis import core, schema

    with pytest.warns(DeprecationWarning):
        from django_oasis import OpenAPI
    assert core.OpenAPI is OpenAPI

    with pytest.warns(DeprecationWarning):
        from django_oasis import Operation
    assert core.Operation is Operation

    with pytest.warns(DeprecationWarning):
        from django_oasis import Resource
    assert core.Resource is Resource

    with pytest.warns(DeprecationWarning):
        from django_oasis import model2schema
    from django_oasis import common

    assert common.model2schema is model2schema

    with pytest.warns(DeprecationWarning):
        from django_oasis.schema import EMPTY

    assert EMPTY is schema.empty

    with pytest.warns(DeprecationWarning):
        from django_oasis.schema import undefined
    assert undefined is schema.empty
