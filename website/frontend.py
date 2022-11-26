from aiohttp.web import RouteTableDef, Request
from aiohttp_jinja2 import template


routes = RouteTableDef()


@routes.get("/")
@template("index.htm.j2")
async def index(_: Request):
    return {}
