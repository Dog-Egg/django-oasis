#: 空
import warnings

empty = type(
    "empty",
    (),
    dict(
        __repr__=lambda _: "empty",
        __bool__=lambda _: False,
    ),
)()


def __getattr__(name):
    if name == "EMPTY":
        warnings.warn(
            "'EMPTY' is deprecated, use 'undefined' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return empty
    if name == "undefined":
        warnings.warn(
            "'undefined' is deprecated, use 'empty' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return empty
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
