import typing as _t

from .parameters import Body as __B
from .parameters import Cookie as __C
from .parameters import CookieItem as __CI
from .parameters import Header as __H
from .parameters import HeaderItem as __HI
from .parameters import Query as __Q
from .parameters import QueryItem as __QI
from .style import Style

Query = _t.cast(_t.Any, __Q)
Cookie = _t.cast(_t.Any, __C)
Header = _t.cast(_t.Any, __H)
Body = _t.cast(_t.Any, __B)
QueryItem = _t.cast(_t.Any, __QI)
CookieItem = _t.cast(_t.Any, __CI)
HeaderItem = _t.cast(_t.Any, __HI)
