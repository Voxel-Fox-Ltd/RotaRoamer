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
                RETURNING 
                    *
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

    # Don't return anything - the page refreshes out of ease
    return json_response(
        {
            "data": {}
        },
        status=200,
    )
