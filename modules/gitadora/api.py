from typing import Optional

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route, Router
from tinydb import where

import utils.card as conv
from core_database import get_db
from modules.webapi import endpoint, read_model


class GFDM_Profile_Main_Items(BaseModel):
    card: str
    pin: str


class GFDM_Profile_Version_Items(BaseModel):
    game_version: int
    name: str
    title: str
    rival_card_ids: list = []


@endpoint
async def gfdm_profiles(request: Request):
    return get_db().table("gitadora_profile").all()


@endpoint
async def gfdm_profile_id(request: Request):
    gitadora_id = request.path_params["gitadora_id"]
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return get_db().table("gitadora_profile").get(where("gitadora_id") == gitadora_id)


@endpoint
async def gfdm_profile_id_patch(request: Request):
    gitadora_id = request.path_params["gitadora_id"]
    item = await read_model(request, GFDM_Profile_Main_Items)
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


@endpoint
async def gfdm_profile_id_version_patch(request: Request):
    gitadora_id = request.path_params["gitadora_id"]
    version = int(request.path_params["version"])
    item = await read_model(request, GFDM_Profile_Version_Items)
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


@endpoint
async def gfdm_card_to_profile(request: Request):
    card = request.path_params["card"]
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


@endpoint
async def dm_scores(request: Request):
    return get_db().table("drummania_scores").all()


@endpoint
async def gf_scores(request: Request):
    return get_db().table("guitarfreaks_scores").all()


@endpoint
async def dm_scores_id(request: Request):
    gitadora_id = request.path_params["gitadora_id"]
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db().table("drummania_scores").search((where("gitadora_id") == gitadora_id))
    )


@endpoint
async def gf_scores_id(request: Request):
    gitadora_id = request.path_params["gitadora_id"]
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db()
        .table("guitarfreaks_scores")
        .search((where("gitadora_id") == gitadora_id))
    )


@endpoint
async def dm_scores_best(request: Request):
    return get_db().table("drummania_scores_best").all()


@endpoint
async def gf_scores_best(request: Request):
    return get_db().table("guitarfreaks_scores_best").all()


@endpoint
async def dm_scores_best_id(request: Request):
    gitadora_id = request.path_params["gitadora_id"]
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db()
        .table("drummania_scores_best")
        .search((where("gitadora_id") == gitadora_id))
    )


@endpoint
async def gf_scores_best_id(request: Request):
    gitadora_id = request.path_params["gitadora_id"]
    gitadora_id = int("".join([i for i in gitadora_id if i.isnumeric()]))
    return (
        get_db()
        .table("guitarfreaks_scores_best")
        .search((where("gitadora_id") == gitadora_id))
    )


@endpoint
async def dm_scores_mcode_all(request: Request):
    mcode = int(request.path_params["mcode"])
    return get_db().table("drummania_scores").search((where("mcode") == mcode))


@endpoint
async def gf_scores_mcode_all(request: Request):
    mcode = int(request.path_params["mcode"])
    return get_db().table("guitarfreaks_scores").search((where("mcode") == mcode))


@endpoint
async def dm_scores_mcode_best(request: Request):
    mcode = int(request.path_params["mcode"])
    return get_db().table("drummania_scores_best").search((where("mcode") == mcode))


@endpoint
async def gf_scores_mcode_best(request: Request):
    mcode = int(request.path_params["mcode"])
    return get_db().table("guitarfreaks_scores_best").search((where("mcode") == mcode))


router = Router(
    routes=[
        Route("/profiles", gfdm_profiles, methods=["GET"]),
        Route("/profiles/{gitadora_id}", gfdm_profile_id, methods=["GET"]),
        Route("/profiles/{gitadora_id}", gfdm_profile_id_patch, methods=["PATCH"]),
        Route(
            "/profiles/{gitadora_id}/{version}",
            gfdm_profile_id_version_patch,
            methods=["PATCH"],
        ),
        Route("/card/{card}", gfdm_card_to_profile, methods=["GET"]),
        Route("/drummania/scores", dm_scores, methods=["GET"]),
        Route("/guitarfreaks/scores", gf_scores, methods=["GET"]),
        Route("/drummania/scores/{gitadora_id}", dm_scores_id, methods=["GET"]),
        Route("/guitarfreaks/scores/{gitadora_id}", gf_scores_id, methods=["GET"]),
        Route("/drummania/scores_best", dm_scores_best, methods=["GET"]),
        Route("/guitarfreaks/scores_best", gf_scores_best, methods=["GET"]),
        Route(
            "/drummania/scores_best/{gitadora_id}",
            dm_scores_best_id,
            methods=["GET"],
        ),
        Route(
            "/guitarfreaks/scores_best/{gitadora_id}",
            gf_scores_best_id,
            methods=["GET"],
        ),
        Route("/drummania/mcode/{mcode}/all", dm_scores_mcode_all, methods=["GET"]),
        Route("/guitarfreaks/mcode/{mcode}/all", gf_scores_mcode_all, methods=["GET"]),
        Route("/drummania/mcode/{mcode}/best", dm_scores_mcode_best, methods=["GET"]),
        Route("/guitarfreaks/mcode/{mcode}/best", gf_scores_mcode_best, methods=["GET"]),
    ]
)
