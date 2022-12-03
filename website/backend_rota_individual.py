from typing import Any

from aiohttp.web import Request, RouteTableDef, json_response, Response
import aiohttp_session
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/api/rotas/{rota_id}")
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

    # Sort out our returnable data
    data = []

    # Open the database so we can get applicable data
    async with vbu.Database() as db:

        # Get the venues from the user
        venues = await db.call(
            """
            SELECT
                id, name, index
            FROM
                venues
            WHERE
                owner_id = $1
            AND
                rota_id = $2
            ORDER BY
                index ASC,
                name ASC
            """,
            login_id, rota_id,
        )

        # Get positions for the venue
        serialized_venue_permissions = []
        for venue in venues:

            # Get the positions for the venue
            positions = await db.call(
                """
                SELECT
                    id, role_id, index, start_time,
                    end_time, notes
                FROM
                    venue_positions
                WHERE
                    venue_id = $1
                ORDER BY
                    index ASC
                """,
                venue["id"],
            )

            # Add the venue to the data
            for position in positions:
                serialized_venue_permissions.append({
                    'id': position['id'],
                    'role': position['role_id'] or None,
                    'index': position['index'],
                    'start': position['start_time'],
                    'end': position['end_time'],
                    'notes': position['notes'],
                })

        data.append({
            'id': venues[0]['id'],
            'name': venues[0]['name'],
            'index': venues[0]['index'],
            'positions': serialized_venue_permissions,
        })

    # Return the venues
    return json_response(
        {
            "data": utils.encode_row_as_json(data),
        },
        status=200,
    )


@routes.put("/api/rotas/{rota_id}")
@utils.requires_login(api_response=True)
async def api_put_rota_venues(request: Request):
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

    # Get the data from the request
    data: Response | list[dict[str, Any]]
    success, data = await utils.try_read_json(request)
    if not success:
        return data
    if not isinstance(data, list):
        return json_response(
            {
                "message": "Invalid data type.",
            },
            status=400,
        )

    # Open a database connection
    async with vbu.Database() as db:

        # Delete the current venues associated with the rota
        await db.call(
            """
            DELETE FROM
                venues
            WHERE
                owner_id = $1
            AND
                rota_id = $2
            """,
            login_id, rota_id,
        )

        # Create each venue given
        venue: dict
        for venue_index, venue in enumerate(data):  # type: ignore
            venue_rows = await db.call(
                """
                INSERT INTO
                    venues
                    (
                        owner_id,
                        rota_id,
                        name,
                        index
                    )
                VALUES
                    (
                        $1,
                        $2,
                        $3,
                        $4
                    )
                RETURNING
                    *
                """,
                login_id, rota_id, venue["name"], venue_index,
            )

            # Add the positions for the venue into the database
            position: dict
            for position_index, position in enumerate(venue["positions"]):  # type: ignore
                await db.call(
                    """
                    INSERT INTO
                        venue_positions
                        (
                            owner_id,
                            rota_id,
                            venue_id,
                            role_id,
                            index,
                            start_time,
                            end_time,
                            notes
                        )
                    VALUES
                        (
                            $1,
                            $2,
                            $3,
                            $4,
                            $5,
                            $6,
                            $7,
                            $8
                        )
                    """,
                    login_id, rota_id, venue_rows[0]["id"],
                    position["role"],  position_index,
                    position["start"], position["end"],
                    position["notes"],
                )

    # Return the venues
    return json_response(
        {
            "message": "Successfully updated venues.",
        },
        status=200,
    )
