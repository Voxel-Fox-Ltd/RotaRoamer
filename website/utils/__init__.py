import functools

from aiohttp.web import Request


__all__ = (
    "requires_login",
)


def requires_login(*, api_response: bool = False):
    def outer(func):
        @functools.wraps(func)
        async def inner(request: Request):
            return await func(request)
        return inner
    return outer
