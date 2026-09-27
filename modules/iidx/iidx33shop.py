from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from tinydb import Query, where

from core_common import E
from core_database import get_db

set_xrpc_defaults(service="local", models=["LDJ"])

@xrpc("IIDX33shop/getname")
async def iidx33shop_getname(ctx: Ctx):
    pcbid = ctx.info["root"].attrib["srcid"]

    op = get_db().table("shop").get(where("pcbid") == pcbid)
    op = {} if op is None else op

    response = E.response(
        E.IIDX33shop(
            cls_opt=0,
            opname=op.get("opname", config.arcade),
            pid=13,
        )
    )

    return response

@xrpc("IIDX33shop/savename")
async def iidx33shop_savename(ctx: Ctx):
    pcbid = ctx.info["root"].attrib["srcid"]
    opname = ctx.info["root"][0].attrib["opname"]

    shop_info = {
        "pcbid": pcbid,
        "opname": opname,
    }

    get_db().table("shop").upsert(shop_info, where("pcbid") == pcbid)

    response = E.response(E.IIDX33shop())

    return response

@xrpc("IIDX33shop/getconvention")
async def iidx33shop_getconvention(ctx: Ctx):

    response = E.response(
        E.IIDX33shop(
            E.valid(1, __type="bool"),
            music_0=-1,
            music_1=-1,
            music_2=-1,
            music_3=-1,
            start_time=0,
            end_time=0,
        )
    )

    return response

@xrpc("IIDX33shop/sentinfo")
async def iidx33shop_sentinfo(ctx: Ctx):

    response = E.response(E.IIDX33shop())

    return response

@xrpc("IIDX33shop/sendescapepackageinfo")
async def iidx33shop_sendescapepackageinfo(ctx: Ctx):

    response = E.response(E.IIDX33shop(expire=1200))

    return response

@xrpc("IIDX33shop/getclosingtime")
async def iidx33shop_getclosingtime(ctx: Ctx):

    response = E.response(
        E.IIDX33shop(
            E.exist(1, __type="bool"),
            *[E.week(cls_opt=0, week=i) for i in range(7)]
        )
    )

    return response

@xrpc("IIDX33shop/saveclosingtime")
async def iidx33shop_saveclosingtime(ctx: Ctx):

    response = E.response(E.IIDX33shop())

    return response
