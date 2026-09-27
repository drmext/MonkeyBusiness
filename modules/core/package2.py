from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service="package2")

@xrpc("package2/list")
async def package2_list(ctx: Ctx):

    response = E.response(E.package2(expire=1200, status=0))

    return response
