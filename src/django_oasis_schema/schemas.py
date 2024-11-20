from __future__ import annotations

import copy
import datetime
import functools
import inspect
import operator
import re
import typing as t
import warnings
from collections.abc import Iterable, Mapping

from dateutil.parser import isoparse

from . import _validators
from .constants import undefined
from .exceptions import ValidationError
from .utils import make_instance
from .utils.hook import HookClassMeta, get_hook, iter_hooks

__all__ = (
    "Schema",
    "Model",
    "String",
    "Float",
    "Integer",
    "Boolean",
    "Date",
    "Datetime",
    "List",
    "Dict",
    "Any",
    "AnyOf",
    "Password",
)


class MetaOptions(Mapping):
    _inherited_attributes = dict(
        data_type=None,
        data_format=None,
    )
    _exclusive_attributes = dict(
        register_as_component=True,
        schema_name=None,
    )

    def __init__(self, cls: "SchemaMeta"):
        allowed_attrs = {
            *self._inherited_attributes,
            *self._exclusive_attributes,
        }

        opts: t.Dict[str, t.Any]
        for parent in (
            base for base in inspect.getmro(cls)[1:] if isinstance(base, SchemaMeta)
        ):
            if hasattr(parent, "meta"):
                opts = dict(parent.meta)
                break
        else:
            opts = self._inherited_attributes.copy()
        opts.update(self._exclusive_attributes)

        metaclass = getattr(cls, "Meta", None)
        if inspect.isclass(metaclass):
            for attr in dir(metaclass):
                if attr.startswith("_"):
                    continue
                assert attr in allowed_attrs, attr
                opts[attr] = getattr(metaclass, attr, opts[attr])
        self._opts = opts

    def __getitem__(self, item):
        return self._opts[item]

    def __len__(self) -> int:
        return len(self._opts)

    def __iter__(self):
        return iter(self._opts)


class SchemaMeta(HookClassMeta):
    def __init__(cls, classname, bases, attrs: dict, **kwargs):
        super().__init__(classname, bases, attrs, **kwargs)
        cls.meta = MetaOptions(cls)


def default_erase(value):
    """
    >>> default_erase('')
    True
    >>> default_erase(' ')
    True
    >>> default_erase(' a ')
    False
    """
    return isinstance(value, str) and not value.strip()


# 字段参数
_FIELD_PARAMETERS = {
    "required",
    "default",
    "erase",
    "attr",
    "alise",
    "read_only",
    "write_only",
}


def _check():
    """检查是否在构建非字段 Schema 时使用了字段参数"""

    def decorator(method):
        @functools.wraps(method)
        def wrapper(self: "Schema", *args, **kwargs):
            if not self._is_field and hasattr(self, "_check_info"):
                field_parameters, stact = self._check_info
                frameinfo = stact[1]
                warnings.warn_explicit(
                    message=f"{', '.join(repr(x) for x in sorted(field_parameters))} are field parameters, but this schema isn't a field.",
                    category=UserWarning,
                    filename=frameinfo.filename,
                    lineno=frameinfo.lineno,
                )
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class Schema(metaclass=SchemaMeta):
    """
    :param attr: |AsField| 设置序列化输入和反序列化输出的字段映射名，默认等于字段名。
    :param alias: |AsField| 设置序列化输出和反序列化输入的字段映射名，默认等于字段名。
    :param read_only: |AsField| 如果为 `True`，则字段在反序列化时不会被使用，默认为 `False`。
    :param write_only: |AsField| 如果为 `True`，则字段在序列化时不会被使用，默认为 `False`。
    :param required: |AsField| 判断字段是否必需提供，默认必需。可设为 `False` 或提供 ``default`` 参数使其变为非必需。
    :param default: |AsField| 如果字段非必需，且设置了默认值，那么反序列化时如未提供该字段数据，则使用该默认值填充。该参数可设为一个无参函数，默认值将使用该函数的结果。
    :param erase: |AsField| 提供一个在反序列化时使用的函数，接受反序列化前的字段值。如函数返回 `True`，则该字段值将视为未定义。默认将空字符串或仅包含空白字符的字符串视为未定义。
    :param nullable: 执行验证时判断数据是否为 `None`。默认 `False`，表示不可以为 `None`。
    :param description: 为 OAS 提供描述内容。
    :param validators: 用于设置反序列化验证函数。

        .. code-block::

            >>> def validate(value):
            ...     if value <= 0:
            ...         raise ValidationError('不是一个正整数')

            >>> Integer(validators=[validate]).deserialize(-1)
            Traceback (most recent call last):
                ...
            django_oasis_schema.exceptions.ValidationError: [{'msgs': ['不是一个正整数']}]
    """

    meta: MetaOptions

    class Meta:
        #: 声明 `OAS Data Type <https://spec.openapis.org/oas/v3.0.3#dataTypes>`_，自动被子类延用。
        data_type: str

        #: 声明 `OAS Data Type Format <https://spec.openapis.org/oas/v3.0.3#dataTypeFormat>`_，自动被子类延用。
        data_format: t.Optional[str]

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.__args = args
        self.__kwargs = kwargs

        # 检查是否在构建非字段 Schema 时使用了字段参数
        received_field_parameters = set(kwargs) & _FIELD_PARAMETERS
        if received_field_parameters:
            self._check_info = (received_field_parameters, inspect.stack())

        return self

    def copy(self, **kwargs):
        """复制一个 Schema 对象。可以修改其初始化的关键字参数。"""
        _kwargs = self.__kwargs.copy()
        _kwargs.update(kwargs)
        return self.__class__(*self.__args, **_kwargs)

    def __init__(
        self,
        *,
        attr: t.Optional[str] = None,
        alias: t.Optional[str] = None,
        read_only: bool = False,
        write_only: bool = False,
        required: t.Optional[bool] = None,
        default: t.Union[t.Any, t.Callable[[], t.Any]] = undefined,
        nullable: bool = False,
        validators: t.Optional[t.List[t.Callable[[t.Any], t.Any]]] = None,
        choices: t.Optional[t.Iterable] = None,
        description: str | None = None,
        clear_value: t.Optional[t.Callable[[t.Any], bool]] = default_erase,
        erase: t.Optional[t.Callable[[t.Any], bool]] = default_erase,
        error_messages: t.Optional[dict] = None,
        after_deserialization: t.Optional[t.Callable] = None,
    ):
        self._model: t.Optional[Model] = None
        self.__name = None
        self.__attr = attr
        self.__alias = alias
        self.read_only = read_only
        self.write_only = write_only
        if read_only and write_only:
            raise ValueError("read_only and write_only cannot both be True.")

        self.__required = required
        self._default = default
        self._description = description
        self.__nullable = nullable
        self.__choices = choices
        self.__error_messages = error_messages or {}

        if clear_value is not default_erase:
            warnings.warn(
                "The `clear_value` argument is deprecated, use `erase` argument instead.",
                DeprecationWarning,
                3,
            )
            self._erase = clear_value
        else:
            self._erase = erase

        self.__after_deserialization = after_deserialization

        self._validators = validators or []
        if choices is not None:
            self._validators.append(_validators.OneOf((choices)))

    @property
    def _name(self) -> str:
        assert self.__name is not None, f"{self!r} is not a field."
        return self.__name

    @_name.setter
    def _name(self, value):
        assert self.__name is None, self.__name
        self.__name = value

    @property
    def _alias(self) -> str:
        return self.__alias or self._name

    @property
    def _attr(self) -> str:
        return self.__attr or self._name

    @property
    def _required(self) -> bool:
        assert self._model is not None
        if self._model._required_fields == "__all__":
            return True

        if self._model._required_fields is None:
            required = self.__required
            if isinstance(required, bool):
                return required
            return self._default is undefined

        return self._name in self._model._required_fields  # type: ignore

    def _create_validation_error(self, key):
        obj = ValidationError(key=key)
        obj.update_error_message(self.__error_messages)
        return obj

    @_check()
    def deserialize(self, value):
        """对数据进行反序列化操作。"""
        if value is None:
            if self.__nullable:
                return value
            else:
                raise ValidationError("The value cannot be null.")

        try:
            value = self._deserialize(value)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError("Deserialization failure.")

        def get_validators():
            # field hook
            if self._model is not None:
                for hook in iter_hooks(self._model, ("as_validator", self._name)):
                    yield hook

            # schema hook
            for hook in iter_hooks(self, ("as_validator", None)):
                yield hook

            # self
            yield from self._validators

        error = ValidationError()
        for validator in get_validators():
            try:
                validator(value)
            except ValidationError as exc:
                error.concat_error(exc)
        if error._nonempty:
            raise error

        if self.__after_deserialization is not None:
            value = self.__after_deserialization(value)

        return value

    def _get_value(self, data):
        """获取待序列化的值。"""

        hook = get_hook(self._model, ("as_getter", self._name))
        if hook:
            return hook(data)

        get = operator.getitem if isinstance(data, Mapping) else getattr
        try:
            return get(data, self._attr)
        except (KeyError, AttributeError):
            if self._required:
                raise
            return undefined

    @property
    def _is_field(self):
        return self._model is not None

    def _deserialize(self, value):
        return value

    @_check()
    def serialize(self, value):
        """对数据进行序列化操作。"""
        try:
            if value is None:
                if self.__nullable:
                    return value
                else:
                    if self._is_field:
                        raise ValueError(f"The field {self._name!r} cannot be {value}.")
                    raise ValueError(f"The value cannot be {value}.")
            return self._serialize(value)
        except Exception as exc:
            raise exc

    def _serialize(self, value):
        return value

    def __openapispec__(self, oas, **kwargs):
        return oas.SchemaObject(
            dict(
                dict(
                    type=self.meta["data_type"],
                    default=(
                        oas.empty
                        if (self._default is undefined or callable(self._default))
                        else self._default
                    ),
                    description=oas.non_empty(self._description),
                    readOnly=self.read_only,
                    writeOnly=self.write_only,
                    enum=oas.non_empty(self.__choices),
                    nullable=self.__nullable,
                    format=oas.non_empty(self.meta["data_format"]),
                ),
                **kwargs,
            )
        )


class FieldMapping(t.Mapping[str, Schema]):
    def __init__(self, **kwargs):
        self.__field_dict = kwargs

    def __getitem__(self, item) -> Schema:
        return self.__field_dict[item]

    def __len__(self):
        return len(self.__field_dict)

    def __iter__(self):
        return iter(self.__field_dict)


class ModelMeta(SchemaMeta):
    _fields: FieldMapping

    def __new__(mcs, classname, bases, attrs: dict):
        fields: t.Dict[str, Schema] = {}

        # inherit fields
        for base in bases:
            if isinstance(base, ModelMeta):
                for field in base._fields.values():
                    fields.setdefault(field._name, field)  # type: ignore

        for name, value in attrs.copy().items():
            if isinstance(value, Schema):
                value._name = name
                fields[name] = value
                del attrs[name]
        attrs["_fields"] = FieldMapping(**fields)
        return super().__new__(mcs, classname, bases, attrs)

    @property
    def fields(self):
        return self._fields


INCLUDE = "include"
EXCLUDE = "exclude"
ERROR = "error"


class Model(Schema, metaclass=ModelMeta):
    """
    :param required_fields: 覆盖原有的字段必需条件配置。设为空列表则所有字段为非必需，也可设为 ``"__all__"`` 指定所有字段为必需。
    :param unknown_fields: 该参数决定了在反序列化时如何处理未知字段。

        .. code-block::

            >>> class User(Model):
            ...     name = String()
            ...     age = Integer()

            >>> data = {'name': '张三', 'age': 24, 'address': '北京'}

        .. code-block::
            :caption: exclude (默认)

            >>> User().deserialize(data)
            {'name': '张三', 'age': 24}

        .. code-block::
            :caption: include

            >>> User(unknown_fields='include').deserialize(data)
            {'name': '张三', 'age': 24, 'address': '北京'}

        .. code-block::
            :caption: error

            >>> User(unknown_fields='error').deserialize(data)
            Traceback (most recent call last):
                ...
            django_oasis_schema.exceptions.ValidationError: [{'msgs': ['Unknown field.'], 'loc': ['address']}]
    """

    class Meta:
        data_type = "object"

    _fields: FieldMapping

    #: Model 的字段映射表
    fields: t.Mapping[str, Schema]

    def __init__(
        self,
        required_fields: t.Union[t.Iterable[str], str, None] = None,
        unknown_fields: str = EXCLUDE,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # unknown fields
        unknown_fields_choices = [INCLUDE, EXCLUDE, ERROR]
        if unknown_fields not in unknown_fields_choices:
            raise ValueError(
                "unknown_fields must be one of "
                f'{", ".join([repr(i) for i in unknown_fields_choices])}.'
            )
        self._unknown_fields = unknown_fields

        # required fields
        if isinstance(required_fields, Iterable) and not isinstance(
            required_fields, str
        ):
            required_fields = set(required_fields)
            unknown_field_names = required_fields - self._fields.keys()
            assert (
                not unknown_field_names
            ), f"Unknown field names: {unknown_field_names}."
        else:
            assert (
                required_fields == "__all__" or required_fields is None
            ), f"Invalid required_fields: {required_fields}."
        self._required_fields = required_fields

        # fields
        fields = {}
        for name, field in self.__class__._fields.items():
            field_copy = copy.copy(field)

            assert field_copy._model is None
            field_copy._model = self

            fields[name] = field_copy
        self._fields = FieldMapping(**fields)

    @staticmethod
    def from_dict(fields: t.Dict[str, Schema]) -> t.Type["Model"]:
        """使用由字段组成的字典生成一个 `Model` 类。"""
        attrs: dict = {k: v for k, v in fields.items() if isinstance(v, Schema)}
        klass = type("GeneratedSchema", (Model,), attrs)

        class InnerSchema(klass):  # type: ignore
            def __repr__(self):
                return repr(fields)

        return InnerSchema

    def _deserialize(self, value: dict):
        data = copy.copy(value)
        del value

        rv = {}
        error = ValidationError()

        for field in self._fields.values():
            if field.read_only:
                continue

            try:
                val = data.pop(field._alias)
            except KeyError:
                val = undefined
            else:
                if field._erase is not None and field._erase(val):
                    val = undefined

            if val is undefined:
                if field._required:
                    error.setitem_error(
                        field._alias,
                        field._create_validation_error(key="required"),
                    )

                default = field._default
                if default is not undefined:
                    rv[field._attr] = default() if callable(default) else default

                continue

            try:
                rv[field._attr] = field.deserialize(val)
            except ValidationError as exc:
                error.setitem_error(field._alias, exc)  # type: ignore

        if self._unknown_fields == EXCLUDE:
            pass
        elif self._unknown_fields == INCLUDE:
            rv.update(data)
        elif self._unknown_fields == ERROR and data:
            for key in data:
                error.setitem_error(key, ValidationError("Unknown field."))

        if error._nonempty:
            raise error

        return rv

    def _serialize(self, value):
        rv = {}
        for field in self._fields.values():
            if field.write_only:
                continue
            field_value = field._get_value(value)
            if field_value is undefined:
                continue
            try:
                rv[field._alias] = field.serialize(field_value)
            except Exception as exc:
                raise exc

        return rv

    def __openapispec__(self, oas, **_):
        required = []
        for field in self._fields.values():
            if field._required:
                required.append(field._alias)

        attr = "$schemaobject"
        if not hasattr(self.__class__, attr):
            properties = {}
            for field in self._fields.values():
                properties[field._alias] = field.__openapispec__(oas)
            setattr(
                self.__class__,
                attr,
                oas.SchemaObject(
                    {
                        "type": "object",
                        "title": self.__class__.__name__,
                        "description": oas.non_empty(self.__doc__),
                        "properties": properties,
                    },
                    key=self.__class__.__module__ + "." + self.__class__.__qualname__,
                ),
            )
        schemaobject = getattr(self.__class__, attr)

        if required:
            return super().__openapispec__(
                oas, type=oas.empty, **{"allOf": [schemaobject, {"required": required}]}
            )
        return schemaobject


class String(Schema):
    """
    :param pattern: 如果设置，则反序列化字符串必需匹配正则表达式。
    :param min_length: 如果设置，则反序列化字符串必须大于等于最小长度。
    :param max_length: 设置设置，则反序列化字符串必须小于等于最大长度。
    """

    class Meta:
        data_type = "string"

    def __init__(
        self,
        *,
        pattern: t.Union[str, re.Pattern, None] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.__min_length = min_length
        self.__max_length = max_length

        # pattern
        self.__pattern = None
        if pattern:
            regexp = _validators.RegExpValidator(pattern)
            self.__pattern = regexp.pattern.pattern
            self._validators.append(regexp)

        # length
        if min_length is not None or max_length is not None:
            self._validators.append(_validators.LengthValidator(min_length, max_length))

    def _deserialize(self, value) -> str:
        return str(value)

    def _serialize(self, value) -> str:
        return str(value)

    def __openapispec__(self, oas, **kwargs):
        return super().__openapispec__(
            oas,
            pattern=oas.non_empty(self.__pattern),
            minLength=oas.non_empty(self.__min_length),
            maxLength=oas.non_empty(self.__max_length),
            **kwargs,
        )


class Number(Schema):
    def __init__(
        self,
        *,
        maximum=None,
        exclusive_maximum=False,
        minimum=None,
        exclusive_minimum=False,
        multiple_of=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.__maximum = maximum
        self.__exclusive_maximum = exclusive_maximum
        self.__minimum = minimum
        self.__exclusive_minimum = exclusive_minimum
        if any(i is not None for i in (maximum, minimum)):
            self._validators.append(
                _validators.RangeValidator(
                    maximum=maximum,
                    exclusive_maximum=exclusive_maximum,
                    minimum=minimum,
                    exclusive_minimum=exclusive_minimum,
                )
            )

        self._multiple_of = multiple_of
        if multiple_of is not None:
            self._validators.append(_validators.MultipleOfValidator(self._multiple_of))

    def __openapispec__(self, oas, **_):
        return super().__openapispec__(
            oas,
            maximum=oas.non_empty(self.__maximum),
            exclusiveMaximum=self.__exclusive_maximum,
            minimum=oas.non_empty(self.__minimum),
            exclusiveMinimum=self.__exclusive_minimum,
            multipleOf=oas.non_empty(self._multiple_of),
        )


class Integer(Number):
    class Meta:
        data_type = "integer"

    def _deserialize(self, value) -> int:
        try:
            f = float(value)
            i = int(f)
            if i != f:
                raise ValueError
        except ValueError:
            raise ValidationError("Not a valid integer.")
        return i

    def _serialize(self, value) -> int:
        return int(value)


class Float(Number):
    class Meta:
        data_type = "number"
        data_format = "float"

    def _deserialize(self, value) -> float:
        return float(value)

    def _serialize(self, value):
        return float(value)


class Boolean(Schema):
    class Meta:
        data_type = "boolean"


class Datetime(Schema):
    """
    :param with_tz: 仅反序列可用，如果为 `True` 要求反序列所得 datetime 对象必须包含时区；如果为 `False` 则不能包含时区。默认为 `None`，不做时区要求。
    """

    class Meta:
        data_type = "string"
        data_format = "date-time"

    def __init__(self, *, with_tz: t.Union[bool, None] = None, **kwargs):
        super().__init__(**kwargs)
        self.__with_tz = with_tz

    def _deserialize(self, value: str) -> datetime.datetime:
        try:
            dt = isoparse(value)
        except (ValueError, TypeError):
            raise ValidationError("Not a valid datetime string.")

        if self.__with_tz is not None:
            if self.__with_tz and dt.utcoffset() is None:
                raise ValidationError("Not support timezone-naive datetime.")
            elif not self.__with_tz and dt.utcoffset() is not None:
                raise ValidationError("Not support timezone-aware datetime.")
        return dt

    def _serialize(self, value: datetime.datetime) -> str:
        return value.isoformat()


class Date(Schema):
    class Meta:
        data_type = "string"
        data_format = "date"

    def _deserialize(self, value) -> datetime.date:
        return isoparse(value).date()


class Any(Schema):
    class Meta:
        data_type = None

    def _deserialize(self, value):
        return value

    def _serialize(self, value):
        return value

    def __openapispec__(self, spec):
        return spec.Protect(super().__openapispec__(spec))


class List(Schema):
    """
    :param item: 定义元素类型，默认为 `Any`。
    :param min_items: 如果设置，则反序列化列表长度必须大于等于最小长度。
    :param max_items: 如果设置，则反序列化列表长度必须小于等于最大长度。
    :param unique_items: 如果为 `True`，则反序列化的所有元素必须唯一，默认 `False`。

    .. code-block::

        >>> from collections import namedtuple

        >>> Book = namedtuple('Book', ['title', 'author'])
        >>> books = [
        ...     Book(title='三体', author='刘慈欣'),
        ...     Book(title='活着', author='余华'),
        ... ]

        >>> class BookSchema(Model):
        ...     title = String()
        ...     author = String()

        >>> List(BookSchema).serialize(books)
        [{'title': '三体', 'author': '刘慈欣'}, {'title': '活着', 'author': '余华'}]
    """

    class Meta:
        data_type = "array"

    def __init__(
        self,
        item: t.Union[Schema, t.Type[Schema], None] = None,
        *,
        min_items: t.Optional[int] = None,
        max_items: t.Optional[int] = None,
        unique_items: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.__min_items = min_items
        self.__max_items = max_items
        self.__unique_items = unique_items
        self._item: Schema = make_instance(item or Any)
        if max_items is not None or min_items is not None:
            self._validators.append(_validators.LengthValidator(min_items, max_items))
        if unique_items:
            self._validators.append(_validators.unique_validate)

    def _deserialize(self, value):
        rv = []
        error = ValidationError()

        for index, item in enumerate(value):
            try:
                rv.append(self._item.deserialize(item))
            except ValidationError as exc:
                error.setitem_error(index, exc)

        if error._nonempty:
            raise error
        return rv

    def _serialize(self, value):
        rv = []
        for item in value:
            rv.append(self._item.serialize(item))
        return rv

    def __openapispec__(self, oas, **_):
        return super().__openapispec__(
            oas,
            items=self._item.__openapispec__(oas),
            maxItems=oas.non_empty(self.__max_items),
            minItems=oas.non_empty(self.__min_items),
            uniqueItems=self.__unique_items,
        )


class Dict(Schema):
    """
    :param value: 定义值类型，默认为 `Any`。
    :param min_properties: 如果设置，则反序列化字典长度必须大于等于最小长度。
    :param max_properties: 如果设置，则反序列化字典长度必须小于等于最大长度。
    """

    class Meta:
        data_type = "object"

    def __init__(
        self,
        value: t.Union[Schema, t.Type[Schema], None] = None,
        *,
        max_properties: t.Optional[int] = None,
        min_properties: t.Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.__max_properties = max_properties
        self.__min_properties = min_properties
        self.__value: Schema = make_instance(value or Any)

        if min_properties is not None or max_properties is not None:
            self._validators.append(
                _validators.LengthValidator(min_properties, max_properties)
            )

    def _deserialize(self, obj):
        if not isinstance(obj, dict):
            raise ValidationError("Not a valid dict object.")
        rv = {}
        err = ValidationError()
        for key, val in obj.items():
            try:
                val = self.__value.deserialize(val)
            except ValidationError as e:
                err.setitem_error(key, e)
            rv[key] = val

        if err._nonempty:
            raise err

        return rv

    def _serialize(self, obj):
        return {key: self.__value.serialize(val) for key, val in obj.items()}

    def __openapispec__(self, oas, **_) -> dict:
        return super().__openapispec__(
            oas,
            additionalProperties=(self.__value.__openapispec__(oas)),
            maxProperties=self.__max_properties,
            minProperties=self.__min_properties,
        )


class AnyOf(Schema):
    def __init__(self, schemas: t.List[Schema], **kwargs) -> None:
        super().__init__(**kwargs)
        self.__schemas = schemas


class Password(String):
    def __init__(self, **kwargs):
        kwargs.setdefault("erase", lambda v: isinstance(v, str) and v == "")
        super().__init__(**kwargs)

    class Meta:
        data_format = "password"
