import uuid

from aiohttp.web import HTTPFound, RouteTableDef, Request
from aiohttp_jinja2 import template
import aiohttp_session
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/")
@template("index.j2")
@utils.add_session()
async def index(_: Request):
    return {}


@routes.get("/logout")
async def logout(request: Request):
    session = await aiohttp_session.get_session(request)
    session.clear()
    session.invalidate()
    return HTTPFound("/")


@routes.get("/login")
@template("login.j2")
@utils.add_session()
async def login(_: Request):
    return {}


@routes.get("/dashboard")
@template("dashboard/index.j2")
@utils.requires_login()
@utils.add_session()
async def dashboard(_: Request):
    return {}


@routes.get("/dashboard/roles")
@template("dashboard/roles.j2")
@utils.requires_login()
@utils.add_session()
async def dashboard_roles(_: Request):
    return {}


@routes.get("/dashboard/people")
@template("dashboard/people.j2")
@utils.requires_login()
@utils.add_session()
async def dashboard_people(_: Request):
    return {}


@routes.get("/dashboard/availability")
@template("dashboard/availability.j2")
@utils.requires_login()
@utils.add_session()
async def dashboard_availability(_: Request):
    return {}


@routes.get("/dashboard/availability/{id}")
@template("dashboard/availability_view.j2")
@utils.requires_login()
@utils.add_session()
async def dashboard_availability_view(request: Request):
    """
    Show the admin the filled out availability for the given ID.
    If the dates on the availability have passed (both start and end), show
    the users at the time.
    If the dates are still yet to happen, show current users only.
    """

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = session.get("id")
    assert login_id, "Missing login ID from session."

    # Verify the given ID exists
    async with vbu.Database() as db:
        rows = await db.call(
            """
            SELECT
                *
            FROM
                availability
            WHERE
                id = $2
            AND
                owner_id = $1
            """,
            login_id, request.match_info['id'],
        )
    if not rows:
        return HTTPFound("/dashboard/availability")

    # And we good - everything else can be AJAXd
    return {}


@routes.get("/dashboard/rotas")
@template("dashboard/rotas.j2")
@utils.requires_login()
@utils.add_session()
async def dashboard_rotas(_: Request):
    return {}


@routes.get("/fill/{id}")
@template("fill.j2")
@utils.add_session()
async def fill_availability(request: Request):
    """
    Show the admin the filled out availability for the given ID.
    If the dates on the availability have passed (both start and end), show
    the users at the time.
    If the dates are still yet to happen, show current users only.
    """

    # Make sure the ID is a valid UUID
    try:
        availability_id = uuid.UUID(request.match_info['id'])
    except:
        return HTTPFound("/")

    # Verify the given ID exists
    async with vbu.Database() as db:
        rows = await db.call(
            """
            SELECT
                filled_availability.availability_id,
                filled_availability.person_id,
                people.name AS person_name,
                filled_availability.availability,
                availability.start_date,
                availability.end_date
            FROM
                filled_availability
            LEFT JOIN
                people
            ON
                people.id = filled_availability.person_id
            LEFT JOIN
                availability
            ON
                availability.id = filled_availability.availability_id
            WHERE
                filled_availability.id = $1
            """,
            availability_id,
        )
    if not rows:
        return HTTPFound("/")

    # And we good - everything else can be AJAXd
    return {
        "person_name": rows[0]['person_name'],
        "person_id": rows[0]['person_id'],
        "start_date": rows[0]['start_date'],
        "end_date": rows[0]['end_date'],
        "current": rows[0]['availability'],
    }
