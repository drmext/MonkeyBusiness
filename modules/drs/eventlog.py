from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local", models=["REC"])

@xrpc("eventlog/write")
async def drs_eventlog_write(ctx: Ctx):

    response = E.response(
        E.eventlog(
            E.gamesession(9999999, __type="s64"),
            E.logsendflg(1 if config.maintenance_mode else 0, __type="s32"),
            E.logerrlevel(0, __type="s32"),
            E.evtidnosendflg(0, __type="s32"),
        )
    )

    return response
