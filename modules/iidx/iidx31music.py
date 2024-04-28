import time
import random
from enum import IntEnum

from fastapi import APIRouter, Request, Response
from tinydb import where

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

import config

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["LDJ"]


class ClearFlags(IntEnum):
    NO_PLAY = 0
    FAILED = 1
    ASSIST_CLEAR = 2
    EASY_CLEAR = 3
    CLEAR = 4
    HARD_CLEAR = 5
    EX_HARD_CLEAR = 6
    FULL_COMBO = 7


@router.post("/{gameinfo}/IIDX31music/getrank")
async def iidx31music_getrank(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0]

    play_style = int(root.attrib["cltype"])

    requested_ids = [
        int(root.get("iidxid", 0)),
        int(root.get("iidxid0", 0)),
        int(root.get("iidxid1", 0)),
        int(root.get("iidxid2", 0)),
        int(root.get("iidxid3", 0)),
        int(root.get("iidxid4", 0)),
        int(root.get("iidxid5", 0)),
    ]

    all_scores = {}
    db = get_db()

    for rival_idx, iidxid in enumerate(requested_ids, -1):
        if iidxid == 0:
            continue

        profile = db.table("iidx_profile").get(where("iidx_id") == iidxid)["version"][
            str(game_version)
        ]

        for record in db.table("iidx_scores_best").search(
            (where("music_id") < (game_version + 1) * 1000)
            & (where("play_style") == play_style)
            & (where("iidx_id") == iidxid)
        ):
            music_id = record["music_id"]
            clear_flg = record["clear_flg"]
            ex_score = record["ex_score"]
            miss_count = record["miss_count"]
            chart_id = record["chart_id"]

            if (rival_idx, music_id) not in all_scores:
                all_scores[rival_idx, music_id] = {
                    0: {"clear_flg": -1, "ex_score": -1, "miss_count": -1},
                    1: {"clear_flg": -1, "ex_score": -1, "miss_count": -1},
                    2: {"clear_flg": -1, "ex_score": -1, "miss_count": -1},
                    3: {"clear_flg": -1, "ex_score": -1, "miss_count": -1},
                    4: {"clear_flg": -1, "ex_score": -1, "miss_count": -1},
                }

            all_scores[rival_idx, music_id][chart_id]["clear_flg"] = clear_flg
            all_scores[rival_idx, music_id][chart_id]["ex_score"] = ex_score
            all_scores[rival_idx, music_id][chart_id]["miss_count"] = miss_count

    names = {}
    profiles = get_db().table("iidx_profile")
    for p in profiles:
        names[p["iidx_id"]] = {}
        try:
            names[p["iidx_id"]]["name"] = p["version"][str(game_version)]["djname"]
        except KeyError:
            names[p["iidx_id"]]["name"] = "UNK"

    top_scores = {}
    for record in db.table("iidx_scores_best").search(
        (where("music_id") < (game_version + 1) * 1000)
        & (where("play_style") == play_style)
    ):
        music_id = record["music_id"]
        ex_score = record["ex_score"]
        chart_id = record["chart_id"]
        iidx_id = record["iidx_id"]

        if music_id not in top_scores:
            top_scores[music_id] = {
                0: {"djname": "", "clear_flg": -1, "ex_score": -1},
                1: {"djname": "", "clear_flg": -1, "ex_score": -1},
                2: {"djname": "", "clear_flg": -1, "ex_score": -1},
                3: {"djname": "", "clear_flg": -1, "ex_score": -1},
                4: {"djname": "", "clear_flg": -1, "ex_score": -1},
            }

        if ex_score > top_scores[music_id][chart_id]["ex_score"]:
            top_scores[music_id][chart_id]["djname"] = names[iidx_id]["name"]
            top_scores[music_id][chart_id]["clear_flg"] = 1
            top_scores[music_id][chart_id]["ex_score"] = ex_score

    response = E.response(
        E.IIDX31music(
            E.style(type=play_style),
            *[
                E.m(
                    [
                        i,
                        k,
                        *[all_scores[i, k][d]["clear_flg"] for d in range(5)],
                        *[all_scores[i, k][d]["ex_score"] for d in range(5)],
                        *[all_scores[i, k][d]["miss_count"] for d in range(5)],
                    ],
                    __type="s16",
                )
                for i, k in all_scores
            ],
            *[
                E.top(
                    E.detail(
                        [
                            k,
                            *[top_scores[k][d]["clear_flg"] for d in range(5)],
                            *[top_scores[k][d]["ex_score"] for d in range(5)],
                        ],
                        __type="s16",
                    ),
                    name0=top_scores[k][0]["djname"],
                    name1=top_scores[k][1]["djname"],
                    name2=top_scores[k][2]["djname"],
                    name3=top_scores[k][3]["djname"],
                    name4=top_scores[k][4]["djname"],
                )
                for k in top_scores
            ],
        )
    )

    assert response is not None

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31music/crate")
async def iidx31music_crate(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    db = get_db()
    all_score_stats = db.table("iidx_score_stats").search(
        (where("music_id") < (game_version + 1) * 1000)
    )

    crate = {}
    fcrate = {}
    for stat in all_score_stats:
        if stat["music_id"] not in crate:
            crate[stat["music_id"]] = [1001] * 10
        if stat["music_id"] not in fcrate:
            fcrate[stat["music_id"]] = [1001] * 10

        if stat["play_style"] == 1:
            dp_idx = 5
        else:
            dp_idx = 0

        crate[stat["music_id"]][stat["chart_id"] + dp_idx] = int(stat["clear_rate"])
        fcrate[stat["music_id"]][stat["chart_id"] + dp_idx] = int(stat["fc_rate"])

    response = E.response(
        E.IIDX31music(*[E.c(crate[k] + fcrate[k], mid=k, __type="s32") for k in crate])
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31music/reg")
async def iidx31music_reg(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    timestamp = time.time()

    log = request_info["root"][0].find("music_play_log")

    clear_flg = int(request_info["root"][0].attrib["cflg"])
    clid = int(request_info["root"][0].attrib["clid"])
    is_death = int(request_info["root"][0].attrib["is_death"])
    pid = int(request_info["root"][0].attrib["pid"])

    play_style = int(log.attrib["play_style"])
    ex_score = int(log.attrib["ex_score"])
    folder_type = int(log.attrib["folder_type"])
    gauge_type = int(log.attrib["gauge_type"])
    graph_type = int(log.attrib["graph_type"])
    great_num = int(log.attrib["great_num"])
    iidx_id = int(log.attrib["iidx_id"])
    miss_num = int(log.attrib["miss_num"])
    mode_type = int(log.attrib["mode_type"])
    music_id = int(log.attrib["music_id"])
    note_id = int(log.attrib["note_id"])
    option1 = int(log.attrib["option1"])
    option2 = int(log.attrib["option2"])
    pgreat_num = int(log.attrib["pgreat_num"])

    ghost = log.find("ghost").text
    ghost_gauge = log.find("ghost_gauge").text

    db = get_db()
    db.table("iidx_scores").insert(
        {
            "timestamp": timestamp,
            "game_version": game_version,
            "iidx_id": iidx_id,
            "pid": pid,
            "clear_flg": clear_flg,
            "is_death": is_death,
            "music_id": music_id,
            "play_style": play_style,
            "chart_id": note_id,
            "pgreat_num": pgreat_num,
            "great_num": great_num,
            "ex_score": ex_score,
            "miss_count": miss_num,
            "folder_type": folder_type,
            "gauge_type": gauge_type,
            "graph_type": graph_type,
            "mode_type": mode_type,
            "option1": option1,
            "option2": option2,
            "ghost": ghost,
            "ghost_gauge": ghost_gauge,
        },
    )

    best_score = db.table("iidx_scores_best").get(
        (where("iidx_id") == iidx_id)
        & (where("play_style") == play_style)
        & (where("music_id") == music_id)
        & (where("chart_id") == note_id)
    )
    best_score = {} if best_score is None else best_score

    if clear_flg < ClearFlags.EASY_CLEAR:
        miss_num = -1
    best_miss_count = best_score.get("miss_count", miss_num)
    if best_miss_count == -1:
        miss_count = max(miss_num, best_miss_count)
    elif clear_flg > ClearFlags.ASSIST_CLEAR:
        miss_count = min(miss_num, best_miss_count)
    else:
        miss_count = best_miss_count
    best_ex_score = best_score.get("ex_score", ex_score)
    best_score_data = {
        "game_version": game_version,
        "iidx_id": iidx_id,
        "pid": pid,
        "play_style": play_style,
        "music_id": music_id,
        "chart_id": note_id,
        "miss_count": miss_count,
        "ex_score": max(ex_score, best_ex_score),
        "ghost": ghost if ex_score >= best_ex_score else best_score.get("ghost", ghost),
        "ghost_gauge": ghost_gauge
        if ex_score >= best_ex_score
        else best_score.get("ghost_gauge", ghost_gauge),
        "clear_flg": max(clear_flg, best_score.get("clear_flg", clear_flg)),
        "gauge_type": gauge_type
        if ex_score >= best_ex_score
        else best_score.get("gauge_type", gauge_type),
    }

    db.table("iidx_scores_best").upsert(
        best_score_data,
        (where("iidx_id") == iidx_id)
        & (where("play_style") == play_style)
        & (where("music_id") == music_id)
        & (where("chart_id") == note_id),
    )

    score_stats = db.table("iidx_score_stats").get(
        (where("music_id") == music_id)
        & (where("play_style") == play_style)
        & (where("chart_id") == note_id)
    )
    score_stats = {} if score_stats is None else score_stats

    score_stats["game_version"] = game_version
    score_stats["play_style"] = play_style
    score_stats["music_id"] = music_id
    score_stats["chart_id"] = note_id
    score_stats["play_count"] = score_stats.get("play_count", 0) + 1
    score_stats["fc_count"] = score_stats.get("fc_count", 0) + (
        1 if clear_flg == ClearFlags.FULL_COMBO else 0
    )
    score_stats["clear_count"] = score_stats.get("clear_count", 0) + (
        1 if clear_flg >= ClearFlags.EASY_CLEAR else 0
    )
    score_stats["fc_rate"] = int(
        (score_stats["fc_count"] / score_stats["play_count"]) * 1000
    )
    score_stats["clear_rate"] = int(
        (score_stats["clear_count"] / score_stats["play_count"]) * 1000
    )

    db.table("iidx_score_stats").upsert(
        score_stats,
        (where("music_id") == music_id)
        & (where("play_style") == play_style)
        & (where("chart_id") == note_id),
    )

    ranklist_data = []
    ranklist_scores = db.table("iidx_scores_best").search(
        (where("play_style") == play_style)
        & (where("music_id") == music_id)
        & (where("chart_id") == note_id)
    )
    ranklist_scores = [] if ranklist_scores is None else ranklist_scores

    ranklist_scores_ranked = []

    for score in ranklist_scores:
        profile = db.table("iidx_profile").get(where("iidx_id") == score["iidx_id"])

        if profile is None or str(game_version) not in profile["version"]:
            continue

        game_profile = profile["version"][str(game_version)]

        ranklist_scores_ranked.append(
            {
                "opname": config.arcade,
                "name": game_profile["djname"],
                "pid": game_profile["region"],
                "back": game_profile.get("back", 0),
                "body": game_profile["body"],
                "face": game_profile["face"],
                "hair": game_profile["hair"],
                "hand": game_profile["hand"],
                "head": game_profile["head"],
                "dgrade": game_profile["grade_double"],
                "sgrade": game_profile["grade_single"],
                "score": score["ex_score"],
                "iidx_id": score["iidx_id"],
                "clflg": score["clear_flg"],
                "myFlg": score["iidx_id"] == iidx_id,
            }
        )

    ranklist_scores_ranked = sorted(
        ranklist_scores_ranked, key=lambda x: (x["clflg"], x["score"]), reverse=True
    )

    myRank = 0
    for rnum, score in enumerate(ranklist_scores_ranked):
        r = E.data(
            rnum=rnum + 1,
            opname=score["opname"],
            name=score["name"],
            pid=score["pid"],
            back=score["back"],
            body=score["body"],
            face=score["face"],
            hair=score["hair"],
            hand=score["hand"],
            head=score["head"],
            dgrade=score["dgrade"],
            sgrade=score["sgrade"],
            score=score["score"],
            iidx_id=score["iidx_id"],
            clflg=score["clflg"],
            myFlg=score["myFlg"],
            achieve=0,
        )
        ranklist_data.append(r)

        if score["myFlg"]:
            myRank = rnum + 1

    response = E.response(
        E.IIDX31music(
            E.ranklist(*ranklist_data, total_user_num=len(ranklist_data)),
            E.shopdata(rank=myRank),
            clid=clid,
            crate=score_stats["clear_rate"],
            frate=score_stats["fc_rate"],
            mid=music_id,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31music/appoint")
async def iidx31music_appoint(request: Request):
    request_info = await core_process_request(request)

    root = request_info["root"][0]

    iidxid = int(root.attrib["iidxid"])
    music_id = int(root.attrib["mid"])
    chart_id = int(root.attrib["clid"])
    ctype = int(root.attrib["ctype"])
    subtype = root.attrib["subtype"]

    db = get_db()
    record = db.table("iidx_scores_best").get(
        (where("iidx_id") == iidxid)
        & (where("music_id") == music_id)
        & (where("chart_id") == chart_id)
    )

    vals = []
    if record is not None:
        vals.append(
            E.mydata(
                record["ghost"],
                score=record["ex_score"],
                __type="bin",
                __size=len(record["ghost"]) // 2,
            )
        )

    if ctype == 1:
        sdata = db.table("iidx_scores_best").get(
            (where("iidx_id") == int(subtype))
            & (where("music_id") == music_id)
            & (where("chart_id") == chart_id)
        )
    elif ctype in (2, 4, 10):
        sdata = {
            "game_version": 29,
            "ghost": "",
            "ex_score": 0,
            "iidx_id": 0,
            "name": "",
            "pid": 13,
        }

        for record in db.table("iidx_scores_best").search(
            (where("music_id") == music_id) & (where("chart_id") == chart_id)
        ):
            if record["ex_score"] > sdata["ex_score"]:
                sdata["game_version"] = record["game_version"]
                sdata["ghost"] = record["ghost"]
                sdata["ex_score"] = record["ex_score"]
                sdata["iidx_id"] = record["iidx_id"]
                sdata["pid"] = record["pid"]

    if ctype in (1, 2, 4, 10) and sdata["ex_score"] != 0:
        vals.append(
            E.sdata(
                sdata["ghost"],
                score=sdata["ex_score"],
                name=db.table("iidx_profile").get(where("iidx_id") == sdata["iidx_id"])[
                    "version"
                ][str(sdata["game_version"])]["djname"],
                pid=sdata["pid"],
                __type="bin",
                __size=len(sdata["ghost"]) // 2,
            )
        )

    response = E.response(E.IIDX31music(*vals))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31music/arenaCPU")
async def iidx31music_arenacpu(request: Request):
    request_info = await core_process_request(request)

    root = request_info["root"][0]
    music_list = root.findall("music_list")
    music_count = len(music_list)
    cpu_list = root.findall("cpu_list")
    cpu_count = len(cpu_list)

    cpu = {}

    for music in music_list:
        music_idx = int(music.find("index").text)
        exscore_max = int(music.find("total_notes").text) * 2

        cpu[music_idx] = {}

        for bot_idx in range(cpu_count):
            cpu[music_idx][bot_idx] = {}

            exscore = round(exscore_max * random.uniform(0.77, 0.93))
            cpu[music_idx][bot_idx]["exscore"] = exscore

            ghost_len = 64
            ghost_data = [0] * ghost_len
            for x in range(ghost_len):
                ghost_data[x] = exscore // ghost_len
                if (exscore % ghost_len) > x:
                    ghost_data[x] += 1

            cpu[music_idx][bot_idx]["ghost_data"] = ghost_data

    response = E.response(
        E.IIDX31music(
            *[
                E.cpu_score_list(
                    E.index(bot_idx, __type="s32"),
                    *[
                        E.score_list(
                            E.index(music_idx, __type="s32"),
                            E.score(cpu[music_idx][bot_idx]["exscore"], __type="s32"),
                            E.ghost(cpu[music_idx][bot_idx]["ghost_data"], __type="s8"),
                            E.enable_score(1, __type="bool"),
                            E.enable_ghost(1, __type="bool"),
                            E.location_id("X000000001", __type="str"),
                        )
                        for music_idx in range(music_count)
                    ],
                )
                for bot_idx in range(cpu_count)
            ],
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31music/retry")
async def iidx31music_retry(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX31music(
            E.session(session_id=1),
            status=0,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31music/play")
async def iidx31music_play(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX31music())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31music/nosave")
async def iidx31music_nosave(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX31music())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
