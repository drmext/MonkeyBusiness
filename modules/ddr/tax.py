from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service="local", models=["MDX"])

@xrpc("tax/get_phase")
async def tax_get_phase(ctx: Ctx):

    response = E.response(
        E.tax(
            E.phase(0, __type="s32"),
        )
    )

    return response
