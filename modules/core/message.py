from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="message")

@xrpc("message/get")
async def message_get(ctx: Ctx):

    response = E.response(
        E.message(
            expire=300,
            *[
                E.item(
                    name=s,
                    start=0,
                    end=604800,
                )
                for s in ("sys.mainte", "sys.eacoin.mainte")
                if config.maintenance_mode
            ]
        )
    )

    return response
