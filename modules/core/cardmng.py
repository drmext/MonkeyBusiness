from fastapi import APIRouter, Request, Response
from tinydb import Query, where

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/core", tags=["cardmng"])


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
        "KDX": "ddr_profile",
        "JDX": "ddr_profile",
        "K32": "gitadora_profile",
        "JDJ": "iidx_profile",
        "I00": "iidx_profile",
        "HDD": "iidx_profile",
        "GLD": "iidx_profile",
        "HDX": "ddr_profile",
        "K33": "gitadora_profile",
        "L32": "gitadora_profile",
        "L33": "gitadora_profile",
        "J32": "gitadora_profile",
        "J33": "gitadora_profile",
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


@router.post("/{gameinfo}/cardmng/authpass")
async def cardmng_authpass(request: Request):
    request_info = await core_process_request(request)

    cid = request_info["root"][0].attrib["refid"]
    passwd = request_info["root"][0].attrib["pass"]

    profile = get_profile(request_info["model"], cid)
    if profile is None or passwd != profile.get("pin", None):
        status = 116
    else:
        status = 0

    response = E.response(E.authpass(status=status))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/cardmng/bindmodel")
async def cardmng_bindmodel(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.bindmodel(dataid=1))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/cardmng/getrefid")
async def cardmng_getrefid(request: Request):
    request_info = await core_process_request(request)

    cid = request_info["root"][0].attrib["cardid"]
    passwd = request_info["root"][0].attrib["passwd"]

    create_profile(request_info["model"], request_info["game_version"], cid, passwd)

    response = E.response(
        E.getrefid(
            dataid=cid,
            refid=cid,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/cardmng/inquire")
async def cardmng_inquire(request: Request):
    request_info = await core_process_request(request)

    cid = request_info["root"][0].attrib["cardid"]

    profile = get_game_profile(request_info["model"], request_info["game_version"], cid)
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

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
