from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local", models=["LDJ", "KDZ", "JDZ"])

@xrpc("ranking/getranker")
async def ranking_getranker(ctx: Ctx):

    response = E.response(E.ranking())

    return response
