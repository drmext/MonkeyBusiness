from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local2", models=["LDJ"])

@xrpc("IIDX31ranking/getranker")
async def iidx31ranking_getranker(ctx: Ctx):

    response = E.response(E.IIDX31ranking())

    return response
