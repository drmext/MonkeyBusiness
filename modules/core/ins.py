from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service="ins")

@xrpc("ins/netlog")
async def ins_netlog(ctx: Ctx):

    response = E.response(E.netlog(status=0))

    return response

@xrpc("ins/send")
async def ins_send(ctx: Ctx):

    response = E.response(E.netlog(status=0))

    return response
