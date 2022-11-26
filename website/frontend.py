from aiohttp.web import RouteTableDef, Request
from aiohttp_jinja2 import template

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


@routes.get("/dashboard/rotas")
@template("dashboard/rotas.j2")
@utils.requires_login()
async def dashboard_rotas(_: Request):
    return {}
