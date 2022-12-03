import functools
from typing import Any, Literal, Optional, Tuple, Mapping, overload
import uuid
from datetime import datetime as dt

from aiohttp.web import Request, HTTPFound, Response, json_response
import aiohttp_session


__all__ = (
    "add_session",
    "requires_login",
    "check_valid_uuid",
    "encode_row_as_json",
    "try_read_json",
    "ensure_required_keys",
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


@overload
def check_valid_uuid(id: str, *,  api_response: bool = False) -> bool:
    ...
@overload
def check_valid_uuid(id: str, *,  api_response: bool = True) -> Optional[Response]:
    ...


def check_valid_uuid(id: str, *, api_response: bool = False) -> Optional[Response] | bool:
    """
    Returns whether or not the given ID is a valid UUID.
    """

    try:
        uuid.UUID(id)
        if api_response:
            return None
        return True
    except:
        if api_response:
            return json_response(
                {
                    "message": "Invalid UUID.",
                },
                status=400,
            )
        return False


@overload
def encode_row_as_json(
        row: dict[str | int, Any],
        key_replacements: Optional[dict[str | int, str]] = None) -> dict:
    ...


@overload
def encode_row_as_json(
        row: list[Any],
        key_replacements: Optional[dict[str | int, str]] = None) -> list:
    ...


def encode_row_as_json(
        row: dict[str | int, Any] |  list[Any],
        key_replacements: Optional[dict[str | int, str]] = None) -> dict | list:
    """
    Encode a row from the database as JSON.
    """

    # Set key replacements up
    key_replacements = key_replacements or dict()

    # Set up output dict
    output = {}

    # Validate input row
    row_is_list = isinstance(row, list)
    if row_is_list:
        row = {
            i: o
            for i, o in enumerate(row)
        }
    assert not isinstance(row, list)

    # Loop through the row and serialize the items in it
    for i, o in row.items():
        new_key = key_replacements.get(i, i)
        if isinstance(o, uuid.UUID):
            output[new_key] = str(o)
        elif isinstance(o, dt):
            output[new_key] = o.isoformat()
        elif isinstance(o, (list, dict)):
            output[new_key] = encode_row_as_json(o)
        elif o is None:
            output[new_key] = None
        else:
            output[new_key] = o

    # Return serialized output
    if row_is_list:
        return list(output.values())
    return output


@overload
async def try_read_json(request: Request) -> Tuple[Literal[False], Response]:
    ...


@overload
async def try_read_json(request: Request) -> Tuple[Literal[True], dict]:
    ...


async def try_read_json(request: Request) -> Tuple[bool, dict | Response]:
    """
    Try to read the request's JSON.
    """

    try:
        return True, await request.json()
    except:
        return False, json_response(
            {
                "message": "Failed to read JSON in request.",
            },
            status=400,
        )


def ensure_required_keys(
        mapping: Mapping,
        required_keys: set[str],
        *,
        location: str = "") -> Response | None:
    """
    Ensure the given mapping has all the required keys.
    Returns either a json response saying the keys are missing, or None.
    """

    missing = []
    for i in required_keys:
        if i not in mapping:
            missing.append(i)
    if missing:
        start = "Invalid request - missing keys"
        if location != "":
            start += f" in {location}"
        return json_response(
            {
                "message": f"{start}: {', '.join(missing)}.",
            },
            status=400,
        )
    return None
