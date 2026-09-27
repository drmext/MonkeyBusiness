from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local2", models=["LDJ"])

@xrpc("IIDX31shop/getname")
async def iidx31shop_getname(ctx: Ctx):

    response = E.response(
        E.IIDX31shop(
            cls_opt=0,
            opname=config.arcade,
            pid=13,
        )
    )

    return response

@xrpc("IIDX31shop/getconvention")
async def iidx31shop_getconvention(ctx: Ctx):

    response = E.response(
        E.IIDX31shop(
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

@xrpc("IIDX31shop/sentinfo")
async def iidx31shop_sentinfo(ctx: Ctx):

    response = E.response(E.IIDX31shop())

    return response

@xrpc("IIDX31shop/sendescapepackageinfo")
async def iidx31shop_sendescapepackageinfo(ctx: Ctx):

    response = E.response(E.IIDX31shop(expire=1200))

    return response
