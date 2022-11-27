from aiohttp.web import HTTPFound, RouteTableDef, Request
from aiohttp_jinja2 import template
import aiohttp_session
from discord.ext import vbu

from . import utils


routes = RouteTableDef()


@routes.get("/")
@template("index.j2")
async def index(_: Request):
    return {}


@routes.get("/dashboard")
@template("dashboard/index.j2")
@utils.requires_login()
async def dashboard(_: Request):
    return {}


@routes.get("/dashboard/roles")
@template("dashboard/roles.j2")
@utils.requires_login()
async def dashboard_roles(_: Request):
    return {}


@routes.get("/dashboard/people")
@template("dashboard/people.j2")
@utils.requires_login()
async def dashboard_people(_: Request):
    return {}


@routes.get("/dashboard/availability")
@template("dashboard/availability.j2")
@utils.requires_login()
async def dashboard_availability(_: Request):
    return {}


@routes.get("/dashboard/availability/{id}")
@template("dashboard/availability_view.j2")
@utils.requires_login()
async def dashboard_availability_view(request: Request):
    """
    Show the admin the filled out availability for the given ID.
    If the dates on the availability have passed (both start and end), show
    the users at the time.
    If the dates are still yet to happen, show current users only.
    """

    # Get the ID of the logged in user
    session = await aiohttp_session.get_session(request)
    login_id = "11b1cdef-d0f1-48b7-8ff6-620f67703a21"  # session.get("id")
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
async def dashboard_rotas(_: Request):
    return {}
