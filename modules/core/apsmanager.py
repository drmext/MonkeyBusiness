from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service="apsmanager")

@xrpc("apsmanager/getstat")
async def apsmanager_getstat(ctx: Ctx):

    response = E.response(E.apsmanager(expire=600))

    return response
