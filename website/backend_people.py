from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
import asyncpg
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/api/people")
@utils.requires_login()
async def api_get_people(request: Request):
    """
    Return a list of people for the user
    """

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
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


@routes.patch("/api/people")
@utils.requires_login()
async def api_patch_person(request: Request):
    """
    Update a person's attributes in the database.
    """

    # Validate the new role
    query = request.query
    required_keys = {"id",}
    if len(required_keys.intersection(set(query.keys()))) != len(required_keys):
        return json_response(
            {
                "message": "Invalid request - missing ID key.",
            },
            status=400,
        )
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
    login_id = session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        rows = await db.call(
            """
            UPDATE
                people
            SET
                name = $3,
                email = $4,
                role_id = $5
            WHERE
                owner_id = $1
            AND
                id = $2
            RETURNING *
            """,
            login_id, query['id'], data['name'],
            data['email'], data['role'],
        )

    # And done
    if not rows:
        return json_response(
            {
                "message": "User not found.",
            },
            status=404,
        )
    return json_response(
        {
            "data": {
                "id": str(rows[0]['id']),
                "name": rows[0]['name'],
                "email": rows[0]['email'],
                "role": str(rows[0]['role_id']) if rows[0]['role_id'] else None,
            }
        },
        status=200,
    )


@routes.delete("/api/people")
@utils.requires_login()
async def api_delete_person(request: Request):
    """
    Delete a person from the database.
    """

    # Validate the new role
    data = request.query
    required_keys = {"id",}
    if len(required_keys.intersection(set(data.keys()))) != len(required_keys):
        return json_response(
            {
                "message": "Invalid request - missing ID key.",
            },
            status=400,
        )

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    async with vbu.Database() as db:
        rows = await db.call(
            """
            DELETE FROM
                people
            WHERE
                owner_id = $1
            AND
                id = $2
            RETURNING *
            """,
            login_id, data['id'],
        )

    # And done
    if not rows:
        return json_response(
            {
                "message": "User not found.",
            },
            status=404,
        )
    return json_response(
        {
            "message": "",
        },
        status=200,
    )


@routes.post("/api/people")
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
    login_id = session.get("id")
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
