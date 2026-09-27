from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local2", models=["LDJ"])

@xrpc("IIDX31streaming/common")
async def iidx31streaming_common(ctx: Ctx):

    response = E.response(E.IIDX31streaming())

    return response

@xrpc("IIDX31streaming/getcm")
async def iidx31streaming_getcm(ctx: Ctx):

    response = E.response(E.IIDX31streaming())

    return response
