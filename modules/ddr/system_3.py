from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

import utils.card as conv

set_xrpc_defaults(service="local2", models=["MDX"])

@xrpc("system_3/convcardnumber")
async def system_3_convcardnumber(ctx: Ctx):
    cid = ctx.info["root"][0].find("data/card_id").text

    response = E.response(
        E.system_3(
            E.data(E.card_number(conv.to_konami_id(cid), __type="str")),
            E.result(0, __type="s32"),
        )
    )

    return response
