from decimal import Decimal

import django
import pytest
from django.db import models

from django_oasis import schema
from django_oasis.common._model2schema import model2schema, parse


class A(models.Model):
    CharField = models.CharField(max_length=12)
    IntegerField = models.IntegerField()
    SmallIntegerField = models.SmallIntegerField()
    DecimalField = models.DecimalField(decimal_places=2, max_digits=5)
    JSONField = models.JSONField()
    FileField = models.FileField()
    TextField = models.TextField()


def assert_parse_model_id(value, other):
    # django 5.0 版本后为 IntegerField 设置了 MinValueValidator、MaxValueValidator 两个验证器。
    _schema, args = value
    args: dict
    assert _schema is schema.Integer
    if django.VERSION >= (5, 0):
        assert (
            str(args.pop("validators"))
            == "[<django_validator_wraps: django.core.validators.MinValueValidator>, <django_validator_wraps: django.core.validators.MaxValueValidator>]"
        )
    assert args == other


def test_A():
    result = parse(A)

    assert_parse_model_id(
        result["id"], {"description": "ID", "read_only": True, "required": False}
    )
    assert result["CharField"] == (schema.String, {"max_length": 12})
    assert_parse_model_id(result["IntegerField"], {})
    assert_parse_model_id(result["SmallIntegerField"], {})
    assert result["JSONField"] == (schema.Any, {})
    assert result["FileField"] == (schema.File, {})
    assert result["TextField"] == (schema.String, {})


class B(models.Model):
    a1 = models.ForeignKey(A, on_delete=models.CASCADE)
    a2 = models.ForeignKey(A, on_delete=models.CASCADE, null=True, verbose_name="A")
    a3 = models.ForeignKey(A, on_delete=models.CASCADE, null=True, default=None)


def test_B():
    result = parse(B)
    assert_parse_model_id(
        result["id"],
        {"description": "ID", "read_only": True, "required": False},
    )
    assert result["a1_id"] == (schema.Integer, {})
    assert result["a2_id"] == (schema.Integer, {"nullable": True, "description": "A"})
    assert result["a3_id"] == (schema.Integer, {"nullable": True, "default": None})


def test_include_exclude_fields():
    """测试 include_fields 中的未知字段。"""

    class FooModel(models.Model):
        a = models.CharField()

    with pytest.raises(ValueError, match="Unknown include_fields: {'b'}."):
        model2schema(FooModel, include_fields=["b"])

    with pytest.raises(ValueError, match="Unknown exclude_fields: {'b'}."):
        model2schema(FooModel, exclude_fields=["b"])


def test_DecimalField():
    class FooModel2(models.Model):
        a = models.DecimalField(max_digits=5)

    FooSchema = model2schema(FooModel2)

    # deserialize
    assert FooSchema().deserialize({"a": 123.12}) == {"a": Decimal("123.12")}

    # deserialize error
    with pytest.raises(schema.ValidationError):
        try:
            FooSchema().deserialize({"a": 123.122})
        except schema.ValidationError as e:
            assert e.format_errors() == [
                {
                    "msgs": ["Ensure that there are no more than 5 digits in total."],
                    "loc": ["a"],
                }
            ]
            raise

    # serialize
    a = FooSchema().serialize({"a": Decimal("1"), "id": 1})["a"]
    assert a == 1 and isinstance(a, int)

    a = FooSchema().serialize({"a": Decimal("1.1"), "id": 1})["a"]
    assert a == 1.1 and isinstance(a, float)

    a = FooSchema().serialize({"a": 1.1, "id": 1})["a"]
    assert a == 1.1 and isinstance(a, float)


class ModelWithFloatField(models.Model):
    float = models.FloatField()


@pytest.mark.django_db
def test_FloatField():
    Schema = model2schema(ModelWithFloatField)
    ModelWithFloatField.objects.create(**Schema().deserialize({"float": 1.2}))
    obj = ModelWithFloatField.objects.get()
    assert Schema().serialize(obj) == {"float": 1.2, "id": 1}
