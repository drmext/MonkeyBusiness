from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local2", models=["MDX"])

@xrpc("eventlog_2/write")
async def ddr_eventlog_2_write(ctx: Ctx):

    response = E.response(
        E.eventlog_2(
            E.gamesession(9999999, __type="s64"),
            E.logsendflg(1 if config.maintenance_mode else 0, __type="s32"),
            E.logerrlevel(0, __type="s32"),
            E.evtidnosendflg(0, __type="s32"),
        )
    )

    return response
