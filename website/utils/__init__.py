__all__ = (
    "requires_login",
)


def requires_login():
    def inner(func):
        return func
    return inner
