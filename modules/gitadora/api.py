from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

from tinydb import Query, where
from core_database import get_db
from pydantic import BaseModel

import config
import utils.card as conv


router = APIRouter(prefix="/gfdm", tags=["api_gfdm"])


class GFDM_Profile_Main_Items(BaseModel):
    card: str
    pin: str


class GFDM_Profile_Version_Items(BaseModel):
    game_version: int
    name: str
    title: str
    rival_card_ids: list = []


@router.get("/profiles")
async def gfdm_profiles():
    return get_db().table("gitadora_profile").all()


@router.get("/profiles/{gitadora_id}")
async def gfdm_profile_id(gitadora_id: str):
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return get_db().table("gitadora_profile").get(where("gitadora_id") == gitadora_id)


@router.patch("/profiles/{gitadora_id}")
async def gfdm_profile_id_patch(gitadora_id: str, item: GFDM_Profile_Main_Items):
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    profile = (
        get_db().table("gitadora_profile").get(where("gitadora_id") == gitadora_id)
    )

    profile["card"] = item.card
    profile["pin"] = item.pin

    get_db().table("gitadora_profile").upsert(
        profile, where("gitadora_id") == gitadora_id
    )
    return Response(status_code=204)


@router.patch("/profiles/{gitadora_id}/{version}")
async def gfdm_profile_id_version_patch(
    gitadora_id: str, version: int, item: GFDM_Profile_Version_Items
):
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    profile = (
        get_db().table("gitadora_profile").get(where("gitadora_id") == gitadora_id)
    )
    game_profile = profile["version"].get(str(version), {})

    game_profile["game_version"] = item.game_version
    game_profile["name"] = item.name
    game_profile["title"] = item.title
    game_profile["rival_card_ids"] = item.rival_card_ids

    profile["version"][str(version)] = game_profile
    get_db().table("gitadora_profile").upsert(
        profile, where("gitadora_id") == gitadora_id
    )
    return Response(status_code=204)


@router.get("/card/{card}")
async def gfdm_card_to_profile(card: str):
    card = card.upper()
    lookalike = {
        "I": "1",
        "O": "0",
        "Q": "0",
        "V": "U",
    }
    for k, v in lookalike.items():
        card = card.replace(k, v)
    if card.startswith("E004") or card.startswith("012E"):
        card = "".join([c for c in card if c in "0123456789ABCDEF"])
        uid = card
        kid = conv.to_konami_id(card)
    else:
        card = "".join([c for c in card if c in conv.valid_characters])
        uid = conv.to_uid(card)
        kid = card
    profile = get_db().table("gitadora_profile").get(where("card") == uid)
    return profile


@router.get("/drummania/scores")
async def dm_scores():
    return get_db().table("drummania_scores").all()


@router.get("/guitarfreaks/scores")
async def gf_scores():
    return get_db().table("guitarfreaks_scores").all()


@router.get("/drummania/scores/{gitadora_id}")
async def dm_scores_id(gitadora_id: str):
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db().table("drummania_scores").search((where("gitadora_id") == gitadora_id))
    )


@router.get("/guitarfreaks/scores/{gitadora_id}")
async def gf_scores_id(gitadora_id: str):
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db()
        .table("guitarfreaks_scores")
        .search((where("gitadora_id") == gitadora_id))
    )


@router.get("/drummania/scores_best")
async def dm_scores_best():
    return get_db().table("drummania_scores_best").all()


@router.get("/guitarfreaks/scores_best")
async def gf_scores_best():
    return get_db().table("guitarfreaks_scores_best").all()


@router.get("/drummania/scores_best/{gitadora_id}")
async def dm_scores_best_id(gitadora_id: str):
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db()
        .table("drummania_scores_best")
        .search((where("gitadora_id") == gitadora_id))
    )


@router.get("/guitarfreaks/scores_best/{gitadora_id}")
async def gf_scores_best_id(gitadora_id: str):
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db()
        .table("guitarfreaks_scores_best")
        .search((where("gitadora_id") == gitadora_id))
    )


@router.get("/drummania/mcode/{mcode}/all")
async def dm_scores_id(mcode: int):
    return get_db().table("drummania_scores").search((where("mcode") == mcode))


@router.get("/guitarfreaks/mcode/{mcode}/all")
async def gf_scores_id(mcode: int):
    return get_db().table("guitarfreaks_scores").search((where("mcode") == mcode))


@router.get("/drummania/mcode/{mcode}/best")
async def dm_scores_id_best(mcode: int):
    return get_db().table("drummania_scores_best").search((where("mcode") == mcode))


@router.get("/guitarfreaks/mcode/{mcode}/best")
async def gf_scores_id_best(mcode: int):
    return get_db().table("guitarfreaks_scores_best").search((where("mcode") == mcode))
