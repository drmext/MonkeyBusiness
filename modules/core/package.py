from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service="package")

@xrpc("package/list")
async def package_list(ctx: Ctx):

    response = E.response(E.package(expire=1200, status=0))

    return response

@xrpc("package/intend")
async def package_intend(ctx: Ctx):

    response = E.response(E.package(status=0))

    return response
