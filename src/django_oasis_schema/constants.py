#: 空
EMPTY = type(
    "EMPTY",
    (),
    dict(
        __repr__=lambda _: "EMPTY",
        __bool__=lambda _: False,
    ),
)()
