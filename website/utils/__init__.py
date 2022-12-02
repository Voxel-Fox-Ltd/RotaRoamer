import functools
from typing import Any
import uuid
from datetime import datetime as dt

from aiohttp.web import Request, HTTPFound, json_response
import aiohttp_session


__all__ = (
    "add_session",
    "requires_login",
    "check_valid_uuid",
    "encode_row_as_json",
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
            session = await aiohttp_session.get_session(request)
            if not session.get("id"):
                if api_response:
                    return json_response(
                        {
                            "message": "You are not logged in.",
                        },
                        status=403,
                    )
                return HTTPFound("/login")
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


def encode_row_as_json(row: dict[str, Any]) -> dict:
    """
    Encode a row from the database as JSON.
    """

    for i, o in row.items():
        if isinstance(o, uuid.UUID):
            row[i] = str(o)
        elif isinstance(o, dt):
            row[i] = o.isoformat()
        elif o is None:
            row[i] = None
    return row
