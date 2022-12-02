import functools
import uuid

from aiohttp.web import Request
import aiohttp_session


__all__ = (
    "add_session",
    "requires_login",
    "check_valid_uuid",
)


def add_session():
    """
    Add the session to the output dict.
    """

    def outer(func):
        @functools.wraps(func)
        async def inner(request: Request):
            v = await func(request)
            if isinstance(v, dict):
                v["session"] = await aiohttp_session.get_session(request)
            return v
        return inner
    return outer


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
