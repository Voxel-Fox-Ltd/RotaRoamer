from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
import asyncpg
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/api/roles")
@utils.requires_login(api_response=True)
async def api_get_roles(request: Request):
    """
    Return a list of roles for the user
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


@routes.delete("/api/roles")
@utils.requires_login(api_response=True)
async def api_delete_role(request: Request):
    """
    Delete a role from the database.
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
                roles
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
                "message": "Role not found.",
            },
            status=404,
        )
    return json_response(
        {
            "message": "",
        },
        status=200,
    )


@routes.post("/api/roles")
@utils.requires_login(api_response=True)
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
    required_keys = {"name", "parent",}
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


@routes.patch("/api/roles")
@utils.requires_login(api_response=True)
async def api_patch_role(request: Request):
    """
    Edit a role
    """

    # Validate the new role
    role_id = request.query.get("id", "")
    if not utils.check_valid_uuid(role_id):
        return json_response(
            {
                "message": "Missing valid role ID from query params.",
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
    required_keys = {"name", "parent",}
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
        added_rows = await db.call(
            """
            UPDATE
                roles
            SET
                name = $3,
                parent_id = $4
            WHERE
                owner_id = $1
            AND
                id = $2
            RETURNING
                id, name, parent_id
            """,
            login_id, role_id, data['name'], data['parent'] or None,
        )
    if not added_rows:
        return json_response(
            {
                "message": "Role does not exist."
            },
            status=404,
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
