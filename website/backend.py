from datetime import datetime as dt
import uuid

from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
import asyncpg
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/api/user_availability")
@utils.requires_login()
async def api_get_user_availability(request: Request):
    """
    Return a dict of users and their related availability for the range of
    time, filling with empty strings.
    This does not check the validity of the given ID.
    """

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
    assert login_id, "Missing login ID from session."

    # Make sure they've given a valid ID.
    availability_id = request.query.get("id")
    if not availability_id:
        return json_response(
            {
                "message": "Missing ID from GET params.",
            },
            status=400,
        )
    try:
        uuid.UUID(availability_id)
    except:
        return json_response(
            {
                "message": "ID given is not a valid UUID.",
            },
            status=400,
        )

    # Get all people's availability
    async with vbu.Database() as db:
        person_rows = await db.call(
            """
            SELECT
                id, name
            FROM
                people
            WHERE
                owner_id = $1
            """,
            login_id,
        )
        availability_rows = await db.call(
            """
            SELECT
                filled_availability.id,
                people.name AS person_name,
                filled_availability.person_id,
                filled_availability.availability
            FROM
                filled_availability
            LEFT JOIN
                people
            ON
                people.id = filled_availability.person_id
            WHERE
                availability_id = $1
            """,
            availability_id,
        )

    # Sort out the availability and names associated
    data = []
    for r in availability_rows:
        data.append({
            "id": str(r['id']),
            "person_name": r['person_name'],
            "person_id": str(r['person_id']),
            "availability": r['availability'],
        })
    return json_response(
        {
            "data": data,
        },
        status=200,
    )


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
    args = [login_id]
    where = ""
    if request.query.get("id"):
        where = "AND id = $2"
        args.append(request.query['id'])
    async with vbu.Database() as db:
        rows = await db.call(
            """
            SELECT
                id, start_date, end_date
            FROM
                availability
            WHERE
                owner_id = $1
            {0}
            """.format(where),
            *args,
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


@routes.post("/api/availability")
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
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
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
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
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


@routes.delete("/api/roles")
@utils.requires_login()
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
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
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


@routes.post("/fill/{id}")
async def post_fill_availability(request: Request):
    """
    Fill the availability for the given user.
    """

    # Make sure the ID is a valid UUID
    try:
        availability_id = uuid.UUID(request.match_info['id'])
    except:
        return json_response(
            {
                "message": "Missing ID from GET params."
            },
            status=400,
        )

    # Get the data
    try:
        data = await request.json()
    except:
        return json_response(
            {
                "message": "Failed to read JSON data."
            },
            status=400,
        )

    # Update data
    async with vbu.Database() as db:
        rows = await db.call(
            """
            UPDATE
                filled_availability
            SET
                availability = $2
            WHERE
                id = $1
            RETURNING
                id
            """,
            availability_id, data,
        )


    if not rows:
        return json_response(
            {
                "message": "Invalid ID."
            },
            status=400,
        )

    # And we good - everything else can be AJAXd
    return json_response(
        {
            "message": "Successfully updated your availability."
        },
        status=200,
    )
