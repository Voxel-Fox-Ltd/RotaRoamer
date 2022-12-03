from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
from discord.ext import vbu
import asyncpg

from . import utils


routes = RouteTableDef()


@routes.get("/api/rotas")
@utils.requires_login(api_response=True)
async def api_get_rotas(request: Request):
    """
    Return all of the JSON data for the venues.
    """

    # Get the user's ID
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID"

    # Get the venues from the user
    async with vbu.Database() as db:
        rotas = await db.call(
            """
            SELECT
                rotas.id,
                availability.id AS availability_id,
                availability.start_date AS start,
                availability.end_date AS end
            FROM
                rotas
            LEFT JOIN
                availability ON rotas.availability_id = availability.id
            WHERE
                rotas.owner_id = $1
            """,
            login_id,
        )

    # Return the venues
    return json_response(
        {
            "data": [
                utils.encode_row_as_json(
                    i,
                    {"availability_id": "availability"},
                )
                for i in rotas
            ],
        },
        status=200,
    )


@routes.post("/api/rotas")
@utils.requires_login(api_response=True)
async def api_post_rotas(request: Request):
    """
    Create a new rota from an availability.
    """

    # Get the user's ID
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID"

    # Validate the request
    success, data = await utils.try_read_json(request)
    if not success:
        return data
    if (r := utils.ensure_required_keys(data, {"availability"}, location="body")):
        return r

    # Get the venues from the user
    async with vbu.Database() as db:
        try:
            rotas = await db.call(
                """
                INSERT INTO
                    rotas
                    (
                        owner_id,
                        availability_id
                    )
                VALUES
                    (
                        $1,
                        $2
                    )
                """,
                login_id, data['availability'],
            )
        except asyncpg.ForeignKeyViolationError:
            return json_response(
                {
                    "error": "Invalid availability ID",
                },
                status=400,
            )

    # Return the venues
    return json_response(
        {
            "data": utils.encode_row_as_json(rotas[0])
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
    if (r := utils.ensure_required_keys(request.query, {"id"}, location="query")):
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
