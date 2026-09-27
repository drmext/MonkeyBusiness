from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

set_xrpc_defaults(service=("local", "local2"), models=["M32"])

@xrpc("{ver}_shopinfo/regist")
async def gitadora_shopinfo_regist(ver: str, ctx: Ctx):

    response = E.response(
        E(
            f"{ver}_shopinfo",
            E.data(
                E.cabid(1, __type="u32"),
                E.locationid("EA000001", __type="str"),
                E.is_send(0, __type="u8"),
            ),
            E.temperature(
                E.is_send(0, __type="bool"),
            ),
            E.tax(
                E.tax_phase(1, __type="s32"),
            ),
        )
    )

    return response
