from datetime import datetime as dt
import uuid

from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
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
    login_id = session.get("id")
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
    if not utils.check_valid_uuid(availability_id):
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
    login_id = session.get("id")
    assert login_id, "Missing login ID from session."

    # Add the new role to the database
    args = [login_id]
    where = ""
    if request.query.get("id"):
        where = "AND id = $2"
        args.append(request.query['id'])
        if not utils.check_valid_uuid(request.query['id']):
            return json_response(
                {
                    "message": "ID given is not a valid UUID.",
                },
                status=400,
            )
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
    login_id = session.get("id")
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
