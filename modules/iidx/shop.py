from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local", models=["LDJ", "KDZ", "JDZ"])

@xrpc("shop/getname")
async def shop_getname(ctx: Ctx):

    response = E.response(
        E.shop(
            cls_opt=0,
            opname=config.arcade,
            pid=13,
        )
    )

    return response

@xrpc("shop/getconvention")
async def shop_getconvention(ctx: Ctx):

    response = E.response(
        E.shop(
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

@xrpc("shop/sentinfo")
async def shop_sentinfo(ctx: Ctx):

    response = E.response(E.shop())

    return response

@xrpc("shop/sendescapepackageinfo")
async def shop_sendescapepackageinfo(ctx: Ctx):

    response = E.response(E.shop(expire=1200))

    return response
