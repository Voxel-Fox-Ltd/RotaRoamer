from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
from discord.ext import vbu

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
        )

    # Return the venues
    return json_response(
        {
            "data": [
                utils.encode_row_as_json(i)
                for i in venues
            ],
        },
        status=200,
    )
