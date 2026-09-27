from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local2", models=["LDJ"])

@xrpc("IIDX29lobby/entry")
async def iidx29lobby_entry(ctx: Ctx):

    response = E.response(E.IIDX29lobby())

    return response

@xrpc("IIDX29lobby/update")
async def iidx29lobby_update(ctx: Ctx):

    response = E.response(E.IIDX29lobby())

    return response

@xrpc("IIDX29lobby/delete")
async def iidx29lobby_delete(ctx: Ctx):

    response = E.response(E.IIDX29lobby())

    return response

@xrpc("IIDX29lobby/bplbattle_entry")
async def iidx29lobby_bplbattle_entry(ctx: Ctx):

    response = E.response(E.IIDX29lobby())

    return response

@xrpc("IIDX29lobby/bplbattle_update")
async def iidx29lobby_bplbattle_update(ctx: Ctx):

    response = E.response(E.IIDX29lobby())

    return response

@xrpc("IIDX29lobby/bplbattle_delete")
async def iidx29lobby_bplbattle_delete(ctx: Ctx):

    response = E.response(E.IIDX29lobby())

    return response
