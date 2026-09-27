from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service="dlstatus")

@xrpc("dlstatus/done")
async def dlstatus_done(ctx: Ctx):

    response = E.response(E.dlstatus(status=0))

    return response

@xrpc("dlstatus/progress")
async def dlstatus_progress(ctx: Ctx):

    response = E.response(E.dlstatus(status=0))

    return response
