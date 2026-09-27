from modules.registry import Ctx, set_xrpc_defaults, xrpc
from tinydb import Query, where

from core_common import E
from core_database import get_db

set_xrpc_defaults(service="cardmng")

def get_target_table(game_id):
    target_table = {
        "LDJ": "iidx_profile",
        "MDX": "ddr_profile",
        "KFC": "sdvx_profile",
        "M32": "gitadora_profile",
        "PAN": "nostalgia_profile",
        "REC": "dancerush_profile",
        "JDZ": "iidx_profile",
        "KDZ": "iidx_profile",
    }

    return target_table[game_id]

def get_profile(game_id, cid):
    target_table = get_target_table(game_id)
    profile = get_db().table(target_table).get(where("card") == cid)

    if profile is None:
        profile = {
            "card": cid,
            "version": {},
        }

    return profile

def get_game_profile(game_id, game_version, cid):
    profile = get_profile(game_id, cid)

    if str(game_version) not in profile["version"]:
        profile["version"][str(game_version)] = {}

    return profile["version"][str(game_version)]

def create_profile(game_id, game_version, cid, pin):
    target_table = get_target_table(game_id)
    profile = get_profile(game_id, cid)

    profile["pin"] = pin

    get_db().table(target_table).upsert(profile, where("card") == cid)

@xrpc("cardmng/authpass")
async def cardmng_authpass(ctx: Ctx):

    cid = ctx.info["root"][0].attrib["refid"]
    passwd = ctx.info["root"][0].attrib["pass"]

    target_table = get_target_table(ctx.info["model"])
    profile = get_db().table(target_table).get(where("card") == cid)
    if profile is None or passwd != profile.get("pin", None):
        status = 116
    else:
        status = 0

    response = E.response(E.authpass(status=status))

    return response

@xrpc("cardmng/bindmodel")
async def cardmng_bindmodel(ctx: Ctx):

    response = E.response(E.bindmodel(dataid=1))

    return response

@xrpc("cardmng/getrefid")
async def cardmng_getrefid(ctx: Ctx):

    cid = ctx.info["root"][0].attrib["cardid"]
    passwd = ctx.info["root"][0].attrib["passwd"]

    create_profile(ctx.info["model"], ctx.info["game_version"], cid, passwd)

    response = E.response(
        E.getrefid(
            dataid=cid,
            refid=cid,
        )
    )

    return response

@xrpc("cardmng/inquire")
async def cardmng_inquire(ctx: Ctx):

    cid = ctx.info["root"][0].attrib["cardid"]

    profile = get_game_profile(ctx.info["model"], ctx.info["game_version"], cid)
    if profile:
        binded = 1
        newflag = 0
        status = 0
    else:
        binded = 0
        newflag = 1
        status = 112

    response = E.response(
        E.inquire(
            dataid=cid,
            ecflag=1,
            expired=0,
            binded=binded,
            newflag=newflag,
            refid=cid,
            status=status,
        )
    )

    return response
