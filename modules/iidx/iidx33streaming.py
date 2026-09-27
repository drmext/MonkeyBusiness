from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local", models=["LDJ"])

@xrpc("IIDX33streaming/common")
async def iidx33streaming_common(ctx: Ctx):

    response = E.response(E.IIDX33streaming())

    return response

@xrpc("IIDX33streaming/getcm")
async def iidx33streaming_getcm(ctx: Ctx):

    response = E.response(E.IIDX33streaming())

    return response
