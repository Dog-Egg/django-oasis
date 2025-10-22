import typing as _t


def set_dict(
    data: dict, path: list[_t.Hashable], setter: _t.Callable[[_t.Any], _t.Any]
):
    d = data
    for index, key in enumerate(path):
        if index == len(path) - 1:
            d[key] = setter(d.get(key))
        else:
            d = d.setdefault(key, {})
    return data
