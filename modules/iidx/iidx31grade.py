import time

from tinydb import Query, where

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["LDJ"]


def get_profile(iidx_id):
    return get_db().table("iidx_profile").get(where("iidx_id") == iidx_id)


@router.post("/{gameinfo}/IIDX31grade/raised")
async def iidx31grade_raised(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    timestamp = time.time()

    iidx_id = int(request_info["root"][0].attrib["iidxid"])
    achi = int(request_info["root"][0].attrib["achi"])
    cstage = int(request_info["root"][0].attrib["cstage"])
    gid = int(request_info["root"][0].attrib["gid"])
    gtype = int(request_info["root"][0].attrib["gtype"])
    is_ex = int(request_info["root"][0].attrib["is_ex"])
    is_mirror = int(request_info["root"][0].attrib["is_mirror"])

    db = get_db()
    db.table("iidx_class").insert(
        {
            "timestamp": timestamp,
            "game_version": game_version,
            "iidx_id": iidx_id,
            "achi": achi,
            "cstage": cstage,
            "gid": gid,
            "gtype": gtype,
            "is_ex": is_ex,
            "is_mirror": is_mirror,
        },
    )

    profile = get_profile(iidx_id)
    game_profile = profile["version"].get(str(game_version), {})

    best_class = db.table("iidx_class_best").get(
        (where("iidx_id") == iidx_id)
        & (where("game_version") == game_version)
        & (where("gid") == gid)
        & (where("gtype") == gtype)
    )

    best_class = {} if best_class is None else best_class

    best_class_data = {
        "game_version": game_version,
        "iidx_id": iidx_id,
        "achi": max(achi, best_class.get("achi", achi)),
        "cstage": max(cstage, best_class.get("cstage", cstage)),
        "gid": gid,
        "gtype": gtype,
        "is_ex": is_ex,
        "is_mirror": is_mirror,
    }

    db.table("iidx_class_best").upsert(
        best_class_data,
        (where("iidx_id") == iidx_id)
        & (where("game_version") == game_version)
        & (where("gid") == gid)
        & (where("gtype") == gtype),
    )

    best_class_plays = db.table("iidx_class_best").search(
        (where("game_version") == game_version) & (where("iidx_id") == iidx_id)
    )

    grades = []
    for record in best_class_plays:
        grades.append(
            [record["gtype"], record["gid"], record["cstage"], record["achi"]]
        )

    game_profile["grade_values"] = grades

    grade_sp = db.table("iidx_class_best").search(
        (where("game_version") == game_version)
        & (where("iidx_id") == iidx_id)
        & (where("gtype") == 0)
        & (where("cstage") == 4)
    )

    game_profile["grade_single"] = max([x["gid"] for x in grade_sp], default=-1)

    grade_dp = db.table("iidx_class_best").search(
        (where("game_version") == game_version)
        & (where("iidx_id") == iidx_id)
        & (where("gtype") == 1)
        & (where("cstage") == 4)
    )

    game_profile["grade_double"] = max([x["gid"] for x in grade_dp], default=-1)

    profile["version"][str(game_version)] = game_profile

    db.table("iidx_profile").upsert(profile, where("game_version") == game_version)

    response = E.response(E.IIDX31grade(pnum=1))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
