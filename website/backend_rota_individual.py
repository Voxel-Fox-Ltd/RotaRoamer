from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/api/rotas/{rota_id}/venues")
@utils.requires_login(api_response=True)
async def api_get_rota_venues(request: Request):
    """
    Get the venues for a given rota.
    """

    # Get the user's ID
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID"

    # Get and validate the rota ID from the url
    rota_id: str = request.match_info["rota_id"]
    if (r := utils.check_valid_uuid(rota_id, api_response=True)):
        return r

    # Get the venues from the user
    async with vbu.Database() as db:
        venues = await db.call(
            """
            SELECT
                id, rota_id, name, index
            FROM
                venues
            WHERE
                owner_id = $1
            AND
                rota_id = $2
            ORDER BY
                index ASC
            """,
            login_id, rota_id,
        )

    # Return the venues
    return json_response(
        {
            "data": [
                utils.encode_row_as_json(
                    i,
                    {"rota_id": "rota"},
                )
                for i in venues
            ],
        },
        status=200,
    )
