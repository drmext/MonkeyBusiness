from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local2", models=["LDJ"])

@xrpc("IIDX30ranking/getranker")
async def iidx30ranking_getranker(ctx: Ctx):

    response = E.response(E.IIDX30ranking())

    return response
