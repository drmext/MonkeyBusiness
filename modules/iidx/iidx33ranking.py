from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local", models=["LDJ"])

@xrpc("IIDX33ranking/getranker")
async def iidx33ranking_getranker(ctx: Ctx):

    response = E.response(E.IIDX33ranking())

    return response
