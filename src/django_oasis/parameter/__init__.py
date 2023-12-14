import typing as _t

from .parameters import (
    Body,
    Cookie,
    CookieItem,
    FormData,
    FormItem,
    Header,
    HeaderItem,
    JsonData,
    Query,
    QueryItem,
)
from .style import Style

Query = _t.cast(_t.Any, Query)
Cookie = _t.cast(_t.Any, Cookie)
Header = _t.cast(_t.Any, Header)
Body = _t.cast(_t.Any, Body)
QueryItem = _t.cast(_t.Any, QueryItem)
CookieItem = _t.cast(_t.Any, CookieItem)
HeaderItem = _t.cast(_t.Any, HeaderItem)
FormData = _t.cast(_t.Any, FormData)
FormItem = _t.cast(_t.Any, FormItem)
JsonData = _t.cast(_t.Any, JsonData)
