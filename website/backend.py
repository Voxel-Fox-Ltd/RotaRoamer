import uuid

from aiohttp.web import Request, RouteTableDef, json_response
import aiohttp_session
from discord.ext import vbu
import asyncpg


routes = RouteTableDef()


@routes.post("/login")
async def post_login(request: Request):
    """
    Handle the login form.
    """

    # Get the form data
    data = await request.json()
    email = data.get("email", "")
    password = data.get("password", "")

    # Check if the username and password are correct
    async with vbu.Database() as db:
        rows = await db.call(
            """
            SELECT
                *
            FROM
                logins
            WHERE
                email = $1
            AND
                pwhash = CRYPT($2, pwhash)
            LIMIT 1
            """,
            email, password,
        )

    # If the username and password are correct, log the user in
    if rows:
        session = await aiohttp_session.new_session(request)
        session["id"] = str(rows[0]["id"])
        return json_response(
            {
                "success": True,
            },
            status=200,
        )

    # Otherwise, return an error
    return json_response(
        {
            "success": False,
        },
        status=401,
    )


@routes.post("/register")
async def post_register(request: Request):
    """
    Handle the register form.
    """

    # Get the form data
    data = await request.json()
    email = data.get("email", "")
    password = data.get("password", "")

    # Check if the username and password are correct
    async with vbu.Database() as db:
        try:
            rows = await db.call(
                """
                INSERT INTO
                    logins
                    (
                        email,
                        pwhash
                    )
                VALUES
                    (
                        $1,
                        CRYPT($2, GEN_SALT('MD5'))
                    )
                RETURNING *
                """,
                email, password,
            )
        except asyncpg.UniqueViolationError:
            return json_response(
                {
                    "success": False,
                    "error": "Email already in use.",
                },
                status=409,
            )

    # If the username and password are correct, log the user in
    session = await aiohttp_session.new_session(request)
    session["id"] = str(rows[0]["id"])
    return json_response(
        {
            "success": True,
        },
        status=200,
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
