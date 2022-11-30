import functools
import uuid

from aiohttp.web import Request


__all__ = (
    "requires_login",
    "check_valid_uuid",
)


def requires_login(*, api_response: bool = False):
    def outer(func):
        @functools.wraps(func)
        async def inner(request: Request):
            return await func(request)
        return inner
    return outer


def check_valid_uuid(id: str) -> bool:
    """
    Returns whether or not the given ID is a valid UUID.
    """

    try:
        uuid.UUID(id)
        return True
    except:
        return False
