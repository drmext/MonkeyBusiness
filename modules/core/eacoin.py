from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from tinydb import where

from core_common import E
from core_database import get_db

sessid = 0
payments = {}

set_xrpc_defaults(service="eacoin")

@xrpc("eacoin/checkin")
async def eacoin_checkin(ctx: Ctx):
    pcbid = ctx.info["root"].attrib["srcid"]
    cardid = ctx.info["root"][0].find("cardid").text

    op = get_db().table("shop").get(where("pcbid") == pcbid)
    op = {} if op is None else op

    bal = get_db().table("paseli").get(where("cardid") == cardid)
    bal = {} if bal is None else bal

    global sessid
    sessid += 1
    payments[sessid] = cardid

    response = E.response(
        E.eacoin(
            E.sequence(1, __type="s16"),
            E.acstatus(1, __type="u8"),
            E.acid(1, __type="str"),
            E.acname(op.get("opname", config.arcade), __type="str"),
            E.balance(bal.get("balance", config.paseli), __type="s32"),
            E.sessid(sessid, __type="str"),
            E.inshopcharge(1, __type="u8"),
        )
    )

    return response

@xrpc("eacoin/checkout")
async def eacoin_checkout(ctx: Ctx):

    response = E.response(E.eacoin())

    return response

@xrpc("eacoin/consume")
async def eacoin_consume(ctx: Ctx):
    sessid = int(ctx.info["root"][0].find("sessid").text)
    payment = int(ctx.info["root"][0].find("payment").text)

    cardid = payments.get(sessid, None)

    # fallback if server is restarted mid-round for IIDX movie or gacha purchases
    if cardid is None:
        return E.response(
            E.eacoin(
                E.acstatus(0, __type="u8"),
                E.autocharge(0, __type="u8"),
                E.balance(config.paseli, __type="s32"),
            )
        )

    bal = get_db().table("paseli").get(where("cardid") == cardid)
    if bal is None:
        bal = {
            "cardid": cardid,
            "balance": config.paseli,
            "total_spent": 0,
        }

    new_balance = bal["balance"] - payment

    paseli_card = {
        "cardid": cardid,
        "balance": new_balance,
        "total_spent": bal["total_spent"] + payment,
    }

    response = E.response(
        E.eacoin(
            E.acstatus(0, __type="u8"),
            E.autocharge(0, __type="u8"),
            E.balance(new_balance, __type="s32"),
        )
    )

    if new_balance < 1000 or new_balance > config.paseli:
        paseli_card["balance"] = config.paseli

    get_db().table("paseli").upsert(paseli_card, where("cardid") == cardid)

    # del payments[sessid]

    return response

@xrpc("eacoin/getbalance")
async def eacoin_getbalance(ctx: Ctx):

    response = E.response(
        E.eacoin(
            E.acstatus(0, __type="u8"),
            E.balance(config.paseli, __type="s32"),
        )
    )

    return response
