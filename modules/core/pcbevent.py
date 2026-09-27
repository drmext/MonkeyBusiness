from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service="pcbevent")

@xrpc("pcbevent/put")
async def pcbevent_put(ctx: Ctx):

    response = E.response(E.pcbevent(expire=600))

    return response
