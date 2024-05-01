#: 空
import warnings

undefined = type(
    "undefined",
    (),
    dict(
        __repr__=lambda _: "undefined",
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
        return undefined
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
