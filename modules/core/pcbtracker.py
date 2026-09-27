from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from time import time

from core_common import E

set_xrpc_defaults(service="pcbtracker")

@xrpc("pcbtracker/alive")
async def pcbtracker_alive(ctx: Ctx):

    response = E.response(
        E.pcbtracker(
            status=0,
            expire=1200,
            ecenable=not config.maintenance_mode,
            eclimit=0,
            limit=0,
            time=int(time()),
        )
    )

    return response
