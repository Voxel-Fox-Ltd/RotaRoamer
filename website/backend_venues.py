from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
from discord.ext import vbu
import asyncpg

from . import utils


routes = RouteTableDef()


@routes.get("/api/venues")
@utils.requires_login(api_response=True)
async def api_get_venues(request: Request):
    """
    Return all of the JSON data for the venues.
    """

    # Get the user's ID
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID"

    # Get the venues from the user
    async with vbu.Database() as db:
        venues = await db.call(
            """
            SELECT
                *
            FROM
                venues
            WHERE
                owner_id = $1
            """,
            login_id,
        )

    # Return the venues
    return json_response(
        {
            "data": [
                utils.encode_row_as_json(
                    i,
                    {"display_name": "display"},
                )
                for i in venues
            ],
        },
        status=200,
    )


@routes.delete("/api/venues")
@utils.requires_login(api_response=True)
async def api_delete_venue(request: Request):
    """
    Delete a venue from the user.
    """

    # Validate the request
    if (r := await utils.ensure_required_keys(request.query, {"id"}, location="query")):
        return r
    if (r := utils.check_valid_uuid(request.query["id"], api_response=True)):
        return r

    # Get the user's ID
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID"

    # Delete the venue
    async with vbu.Database() as db:
        venue_rows = await db.call(
            """
            DELETE FROM
                venues
            WHERE
                owner_id = $1
            AND
                id = $2
            RETURNING
                *
            """,
            login_id, request.query["id"],
        )

    # Return if we've been successful
    if not venue_rows:
        return json_response(
            {
                "message": "Venue not found.",
            },
            status=404,
        )
    return json_response(
        {
            "message": "Venue deleted.",
        },
        status=200,
    )


@routes.post("/api/venues")
@utils.requires_login(api_response=True)
async def api_create_venue(request: Request):
    """
    Deal with creating a new venue.
    """

    # Get and validate the JSON data from the user
    success, data = await utils.try_read_json(request)
    if not success:
        return data
    if (r := await utils.ensure_required_keys(data, {"name"})):
        return r

    # Get the user's ID
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID"

    # Create the venue
    async with vbu.Database() as db:
        try:
            venue_rows = await db.call(
                """
                INSERT INTO
                    venues
                    (
                        owner_id,
                        name,
                        display_name
                    )
                VALUES
                    (
                        $1,
                        $2,
                        $3
                    )
                RETURNING
                    *
                """,
                login_id, data["name"], data.get("display_name", None)
            )
        except asyncpg.UniqueViolationError:
            return json_response(
                {
                    "message": "You already have a venue with that name.",
                },
                status=409,
            )

    # Tell the user it's been created
    return json_response(
        {
            "message": "Venue created.",
            "data": utils.encode_row_as_json(
                venue_rows[0],
                {"display_name": "display"},
            ),
        },
        status=201,
    )


@routes.patch("/api/venues")
@utils.requires_login(api_response=True)
async def api_patch_venue(request: Request):
    """
    Deal with editing an existing venue.
    """

    # Get and validate the JSON data from the user
    success, data = await utils.try_read_json(request)
    if not success:
        return data
    if (r := await utils.ensure_required_keys(request.query, {"id"}, location="query")):
        return r
    if (r := await utils.ensure_required_keys(data, {"name", "dipslay"}, location="body")):
        return r
    if (r := utils.check_valid_uuid(request.query["id"], api_response=True)):
        return r

    # Get the user's ID
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID"

    # Update the venue
    async with vbu.Database() as db:
        try:
            venue_rows = await db.call(
                """
                UPDATE
                    venues
                SET
                    name = $3,
                    display_name = $4
                WHERE
                    owner_id = $1
                AND
                    id = $2
                RETURNING
                    *
                """,
                login_id, request.query["id"],
                data["name"], data["display"],
            )
        except asyncpg.UniqueViolationError:
            return json_response(
                {
                    "message": "You already have a venue with that name.",
                },
                status=409,
            )

    # Tell the user if there was no venue with that ID
    if not venue_rows:
        return json_response(
            {
                "message": "That venue does not exist.",
            },
            status=404,
        )

    # Tell the user it's been created
    return json_response(
        {
            "message": "Venue created.",
            "data": utils.encode_row_as_json(
                venue_rows[0],
                {"display_name": "display"},
            ),
        },
        status=201,
    )
