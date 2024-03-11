import typing as _t

from .parameters import Body as __Body
from .parameters import Cookie as __Cookie
from .parameters import CookieItem as __CookieItem
from .parameters import FormData as __FormData
from .parameters import FormItem as __FormItem
from .parameters import Header as __Header
from .parameters import HeaderItem as __HeaderItem
from .parameters import JsonData as __JsonData
from .parameters import Query as _Query
from .parameters import QueryItem as __QueryItem
from .style import Style

Query = _t.cast(_t.Any, _Query)
Cookie = _t.cast(_t.Any, __Cookie)
Header = _t.cast(_t.Any, __Header)
Body = _t.cast(_t.Any, __Body)
QueryItem = _t.cast(_t.Any, __QueryItem)
CookieItem = _t.cast(_t.Any, __CookieItem)
HeaderItem = _t.cast(_t.Any, __HeaderItem)
FormData = _t.cast(_t.Any, __FormData)
FormItem = _t.cast(_t.Any, __FormItem)
JsonData = _t.cast(_t.Any, __JsonData)
