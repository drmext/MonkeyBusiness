from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from core_common import E

set_xrpc_defaults(service="local2", models=["MDX"])

@xrpc("wordcheck_3/tabooword_check")
async def wordcheck_3_tabooword_check(ctx: Ctx):

    response = E.response(
        E.wordcheck_3(
            E.result(0, __type="s32"),
            E.is_taboo(0, __type="bool"),
        )
    )

    return response
