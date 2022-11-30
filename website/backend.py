import uuid

from aiohttp.web import Request, RouteTableDef, json_response
from discord.ext import vbu


routes = RouteTableDef()


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
