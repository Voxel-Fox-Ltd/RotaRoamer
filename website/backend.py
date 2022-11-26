from datetime import datetime as dt

from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
import asyncpg
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/api/availability")
@utils.requires_login()
async def api_get_availbility(request: Request):
    """
    Return a list of availability objects for the user
    """

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        rows = await db.call(
            """
            SELECT
                id, start_date, end_date
            FROM
                availability
            WHERE
                owner_id = $1
            """,
            login_id,
        )

    # And done
    ret = []
    for r in rows:
        ret.append({
            "id": str(r['id']),
            "start": r['start_date'].isoformat(),
            "end": r['end_date'].isoformat(),
        })
    return json_response(
        {
            "data": ret,
        },
        status=200,
    )


@routes.post("/api/create_availability")
@utils.requires_login()
async def api_post_create_availability(request: Request):
    """
    Add a new availability date set.
    """

    # Validate the new role
    try:
        data = await request.json()
    except:
        return json_response(
            {
                "message": "Failed to read JSON in request.",
            },
            status=400,
        )
    required_keys = {"start", "end",}
    if len(required_keys.intersection(set(data.keys()))) != len(required_keys):
        return json_response(
            {
                "message": "Invalid request - missing keys.",
            },
            status=400,
        )

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        added_rows = await db.call(
            """
            INSERT INTO
                availability
                (
                    owner_id,
                    start_date,
                    end_date
                )
            VALUES
                (
                    $1,
                    $2,
                    $3
                )
            RETURNING
                id, start_date, end_date
            """,
            login_id,
            dt.fromisoformat(data['start'].replace("Z", "")),
            dt.fromisoformat(data['end'].replace("Z", "")),
        )

    # And done
    added_row = dict(added_rows[0])
    added_row["id"] = str(added_row.pop("id"))
    added_row["start"] = added_row.pop("start_date").isoformat()
    added_row["end"] = added_row.pop("end_date").isoformat()
    return json_response(
        {
            "data": added_row,
        },
        status=201,
    )


@routes.get("/api/people")
@utils.requires_login()
async def api_get_people(request: Request):
    """
    Return a list of people for the user
    """

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        rows = await db.call(
            """
            SELECT
                id, name, email, role_id
            FROM
                people
            WHERE
                owner_id = $1
            """,
            login_id,
        )

    # And done
    ret = []
    for r in rows:
        ret.append({
            "id": str(r['id']),
            "name": r['name'],
            "email": r['email'],
            "role": str(r['role_id']) if r['role_id'] else None,
        })
    return json_response(
        {
            "data": ret,
        },
        status=200,
    )


@routes.post("/api/create_person")
@utils.requires_login()
async def api_post_create_person(request: Request):
    """
    Add a new role into the user's list of roles.
    """

    # Validate the new role
    try:
        data = await request.json()
    except:
        return json_response(
            {
                "message": "Failed to read JSON in request.",
            },
            status=400,
        )
    required_keys = {"name", "email", "role",}
    if len(required_keys.intersection(set(data.keys()))) != len(required_keys):
        return json_response(
            {
                "message": "Invalid request - missing keys.",
            },
            status=400,
        )

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        try:
            added_rows = await db.call(
                """
                INSERT INTO
                    people
                    (
                        owner_id,
                        name,
                        email,
                        role_id
                    )
                VALUES
                    (
                        $1,
                        $2,
                        $3,
                        $4
                    )
                RETURNING
                    id, name, email, role_id
                """,
                login_id, data['name'], data['email'], data['role'],
            )
        except asyncpg.UniqueViolationError:
            return json_response(
                {
                    "message": "Cannot add duplicate email."
                },
                status=400,
            )

    # And done
    added_row = dict(added_rows[0])
    added_row["id"] = str(added_row.pop("id"))
    added_row["role"] = str(added_row.pop("role_id"))
    return json_response(
        {
            "data": added_row,
        },
        status=201,
    )


@routes.get("/api/roles")
@utils.requires_login()
async def api_get_roles(request: Request):
    """
    Return a list of roles for the user
    """

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        rows = await db.call(
            """
            SELECT
                id, name, parent_id
            FROM
                roles
            WHERE
                owner_id = $1
            """,
            login_id,
        )

    # And done
    ret = []
    for r in rows:
        ret.append({
            "id": str(r['id']),
            "name": r['name'],
            "parent": str(r['parent_id']) if r['parent_id'] else None,
        })
    return json_response(
        {
            "data": ret,
        },
        status=200,
    )


@routes.post("/api/create_role")
@utils.requires_login()
async def api_post_create_role(request: Request):
    """
    Add a new role into the user's list of roles.
    """

    # Validate the new role
    try:
        data = await request.json()
    except:
        return json_response(
            {
                "message": "Failed to read JSON in request.",
            },
            status=400,
        )
    required_keys = {"name",}
    if len(required_keys.intersection(set(data.keys()))) != len(required_keys):
        return json_response(
            {
                "message": "Invalid request - missing keys.",
            },
            status=400,
        )

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        try:
            added_rows = await db.call(
                """
                INSERT INTO
                    roles
                    (
                        owner_id,
                        name,
                        parent_id
                    )
                VALUES
                    (
                        $1,
                        $2,
                        $3
                    )
                RETURNING
                    id, name, parent_id
                """,
                login_id, data['name'], data['parent'] or None,
            )
        except asyncpg.UniqueViolationError:
            return json_response(
                {
                    "message": "Cannot add duplicate name."
                },
                status=400,
            )

    # And done
    added_row = dict(added_rows[0])
    added_row["id"] = str(added_row.pop("id"))
    added_row["parent"] = (
        str(added_row.pop("parent_id"))
        if added_row.get("parent_id")
        else None
    )
    return json_response(
        {
            "data": added_row,
        },
        status=201,
    )
