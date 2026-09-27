from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local", models=["LDJ"])

@xrpc("IIDX32streaming/common")
async def iidx32streaming_common(ctx: Ctx):

    response = E.response(E.IIDX32streaming())

    return response

@xrpc("IIDX32streaming/getcm")
async def iidx32streaming_getcm(ctx: Ctx):

    response = E.response(E.IIDX32streaming())

    return response
