import random
import time

from tinydb import Query, where

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

from os import path
import json

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["MDX"]


def get_profile(cid):
    return get_db().table("ddr_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


mdb = {}
ddr_metadata = path.join("webui", "ddr.json")
if path.exists(ddr_metadata):
    with open(ddr_metadata, "r", encoding="utf-8") as fp:
        mdb = json.load(fp)

    music_load = []
    for i in sorted(list(mdb.keys()), reverse=True):
        info = mdb[i]
        for idx, lvl in enumerate(info["diffLv"]):
            if int(lvl) != 0:
                music_load.append(f"{i},{1 if idx > 4 else 0},{idx % 5},0,{lvl}")

load_settings = {
    "common": {
        "dancername": "str",
        "area": "s32",
        "extrastar": "s32",
        "playcount": "s32",
        "weight": "s32",
        "today_cal": "u64",
        "is_disp_weight": "bool",
        "is_takeover": "bool",
        "pre_playable_num": "s32",
        "is_subscribed": "bool",
        "popup_subscribe_enable": "bool",
        "popup_subscribe_disable": "bool",
    },
    "option": {
        "hispeed": "s32",
        "gauge": "s32",
        "fastslow": "s32",
        "guideline": "s32",
        "stepzone": "s32",
        "timing_disp": "s32",
        "visibility": "s32",
        "visible_time": "s32",
        "lane": "s32",
        "lane_hiddenpos": "s32",
        "lane_suddenpos": "s32",
        "lane_hidsudpos": "s32",
        "lane_filter": "s32",
        "scroll_direction": "s32",
        "scroll_moving": "s32",
        "arrow_priority": "s32",
        "arrow_placement": "s32",
        "arrow_color": "s32",
        "arrow_design": "s32",
        "cut_timing": "s32",
        "cut_freeze": "s32",
        "cut_jump": "s32",
        "speed_type": "s32",
        "real_speed": "s32",
        "lane_preview": "s32",
        "combo_priority": "s32",
        "judge_priority": "s32",
        "judge_position": "s32",
        "timing_music": "s32",
    },
    "lastplay": {
        "mode": "s32",
        "folder": "s32",
        "mcode": "s32",
        "style": "s32",
        "difficulty": "s32",
        "window_main": "s32",
        "window_sub": "s32",
        "target": "s32",
        "tab_main": "s32",
        "tab_sub": "s32",
        "tab_main_graph_type": "s32",
        "tab_main_graph_disp": "s32",
        "tab_sub_graph_type": "s32",
        "tab_sub_graph_disp": "s32",
    },
    "filtersort": {
        "title": "u64",
        "version": "u64",
        "genre": "u64",
        "bpm": "u64",
        "event": "u64",
        "level": "u64",
        "flare_rank": "u64",
        "clear_rank": "u64",
        "flare_skill_target": "u64",
        "rival_flare_skill": "u64",
        "rival_score_rank": "u64",
        "sort_type": "u64",
        "order_type": "s32",
        "is_quickmode": "bool",
        "cleartype": "u64",
        "difficulty": "u64",
    },
    "checkguide": {
        "tips_basic": "u64",
        "tips_option": "u64",
        "tips_event": "u64",
        "tips_gimmick": "u64",
        "tips_advance": "u64",
        "guide_scene": "u64",
    },
    "brave": {
        "last_braveid": "s32",
        "last_window_btn": "s32",
    },
}

customize_settings = {
    "1": {
        "0": -1, #appeal_board
    },
    "2": {
        "1": -1, #character_left
        "2": -1, #character_right
    },
    "3": {
        "1": -1, #game_bg_system
        "2": -1, #game_bg_play
    },
    "4": {
        "0": -1, #lane_bg_single
    },
    "5": {
        "0": -1, #lane_bg_double
    },
    "6": {
        "0": -1, #lane_cover_single
    },
    "7": {
        "0": -1, #lane_cover_double
    },
    "8": {
        "0": -1, #song_vid
    },
}

flares = [
    (995000, 10),
    (990000, 9),
    (980000, 8),
    (970000, 7),
    (960000, 6),
    (955000, 5),
    (930000, 4),
    (900000, 3),
    (850000, 2),
    (800000, 1),
]

@router.post("/{gameinfo}/playdata_3/musicdata_load")
async def playdata_3_musicdata_load(request: Request):
    request_info = await core_process_request(request)

    if mdb:
        response = E.response(
            E.playdata_3(
                E.result(0, __type="s32"),
                E.servertime(round(time.time() * 1000), __type="u64"),
                *[
                    E.music(
                        E.music_str(s, __type="str"),
                    )
                    for s in music_load
                ],
            )
        )


    else:
        response = E.response(
            E.playdata_3(
                E.result(0, __type="s32"),
                E.servertime(round(time.time() * 1000), __type="u64"),
                E.music(
                    E.music_str("", __type="str"),
                ),
            )
        )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post("/{gameinfo}/playdata_3/playerdata_load")
async def playdata_3_playerdata_load(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    data = request_info["root"][0].find("data")
    #mode = data.find("mode").text
    #gamesession = data.find("gamesession").text
    refid = data.find("refid").text

    default = "X0000000000000000000000000000000"

    all_scores = {}
    if refid != default:
        p = get_profile(refid)
        if p is not None:
            ddr_id = p["ddr_id"]
            profile = get_game_profile(refid, game_version)

            for record in get_db().table("ddr_scores_best").search(where("ddr_id") == ddr_id):
                mcode = record["mcode"]
                difficulty = int(record["difficulty"])
                score = int(record["score"])
                flare = int(record.get("flare_force", 0))
                if flare in (-1, 0):
                    for k, v in flares:
                        if score >= k:
                            flare = v
                            break

                if mcode not in all_scores:
                    all_scores[mcode] = {}
                all_scores[mcode][difficulty] = (
                    f"{difficulty - 4 if difficulty > 4 else difficulty},"
                    f"1,{record['rank']},{record['lamp']},{score},"
                    f"{record['ghostid']},{flare},{flare},0"
                )
    else:
        p = {}
        profile = {}

    response = E.response(
        E.playdata_3(
            E.result(0, __type="s32"),
            E.refid(refid, __type="str"),
            E.gamesession(1, __type="s64"),
            E.servertime(round(time.time() * 1000), __type="u64"),
            E.is_locked(0, __type="bool"),
            E.common(
                E.ddrcode(p.get("ddr_id", 0), __type="s32"),
                E.dancername(profile.get("common_dancername", ""), __type="str"),
                E.is_new(not profile, __type="bool"),
                E.is_registering(0, __type="bool"),
                E.area(profile.get("common_area", 13), __type="s32"),
                E.extrastar(profile.get("common_extrastar", 0), __type="s32"),
                E.playcount(profile.get("common_playcount", 0), __type="s32"),
                E.weight(profile.get("common_weight", 0), __type="s32"),
                E.today_cal(profile.get("common_today_cal", 0), __type="u64"),
                E.is_disp_weight(profile.get("common_is_disp_weight", 0), __type="bool"),
                E.is_takeover(0, __type="bool"),
                E.pre_playable_num(1, __type="s32"),
                E.is_subscribed(1, __type="bool"),
                E.popup_subscribe_enable(0, __type="bool"),
                E.popup_subscribe_disable(0, __type="bool"),
            ),
            *[
                E(k,
                    *[
                        E(v, profile.get(f"{k}_{v}", 0), __type=load_settings[k][v])
                        for v in load_settings[k]
                    ],
                )
                for k in load_settings if k != "common"
            ],
            *[
                E.rival(
                    E.slot(i, __type="s32"),
                    E.rivalcode(profile.get(f"rival_{i}_ddr_id", 0), __type="s32"),
                )
                for i in range (1, 4)
            ],
            *[
                E.score(
                    E.mcode(int(mcode), __type="s32"),
                    *[
                        E.score_single(E.score_str(all_scores[mcode][difficulty], __type="str")) 
                        for difficulty in all_scores[mcode] if difficulty < 5
                    ],
                    *[
                        E.score_double(E.score_str(all_scores[mcode][difficulty], __type="str"))
                        for difficulty in all_scores[mcode] if difficulty > 4
                    ],
                    
                )
                for mcode in all_scores.keys()
            ],
            E.event(
                E.event_str("1,101,0,0,14,0,0", __type="str"),
            ),
            *[
                E.event(
                    E.event_str(f"{x},9999,0,0,0,0,0", __type="str"),
                )
                for x in [
                    e
                    for e in range(101, 1, -1)
                    if e not in [4, 6, 7, 8, 14, 47, 90]
                ]
            ],
            #E.league(),
            #E.current(),
            *[
                E.customize(
                    E.category(c, __type="s32"),
                    E.key(profile["customize"][c][p], __type="s32"),
                    E.pattern(p, __type="s32")
                )
                for c in profile.get("customize", {})
                for p in profile.get("customize", {}).get(c, {})
            ],
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post("/{gameinfo}/playdata_3/rivaldata_load")
async def playdata_3_rivaldata_load(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    data = request_info["root"][0].find("data")
    loadflag = int(data.find("loadkind").text)
    country = data.find("country").text
    region = data.find("region").text
    customercode = data.find("customercode").text
    companycode = data.find("companycode").text
    locationid = data.find("locationid").text
    pcbid = data.find("pcbid").text
    targettime = data.find("targettime").text
    ddrcode = int(data.find("ddrcode").text)

    db = get_db()

    if loadflag == 1:
        all_scores = {}
        for record in db.table("ddr_scores").search(where("ddr_id") != 0):
            ddr_id = record["ddr_id"]
            mcode = record["mcode"]
            difficulty = record["difficulty"]
            score = record["score"]

            if (mcode, difficulty) not in all_scores or score > all_scores[
                (mcode, difficulty)
            ].get("score"):
                all_scores[mcode, difficulty] = {
                    "game_version": game_version,
                    "ddr_id": ddr_id,
                    "mcode": mcode,
                    "difficulty": difficulty,
                    "rank": record["rank"],
                    "lamp": record["lamp"],
                    "score": score,
                    "exscore": record["exscore"],
                    "ghostid": record.doc_id,
                }
        scores = list(all_scores.values())

    elif loadflag == 2:
        all_scores = {}
        for record in db.table("ddr_scores").search(
            (where("shoparea") == region)
            & (where("ddr_id") != 0)
        ):
            ddr_id = record["ddr_id"]
            mcode = record["mcode"]
            difficulty = record["difficulty"]
            score = record["score"]

            if (mcode, difficulty) not in all_scores or score > all_scores[
                (mcode, difficulty)
            ].get("score"):
                all_scores[mcode, difficulty] = {
                    "game_version": game_version,
                    "ddr_id": ddr_id,
                    "mcode": mcode,
                    "difficulty": difficulty,
                    "rank": record["rank"],
                    "lamp": record["lamp"],
                    "score": score,
                    "exscore": record["exscore"],
                    "ghostid": record.doc_id,
                }
        scores = list(all_scores.values())

    elif loadflag == 3:
        all_scores = {}
        for record in db.table("ddr_scores").search(
            (where("pcbid") == pcbid)
            & (where("ddr_id") != 0)
        ):
            ddr_id = record["ddr_id"]
            mcode = record["mcode"]
            difficulty = record["difficulty"]
            score = record["score"]

            if (mcode, difficulty) not in all_scores or score > all_scores[
                (mcode, difficulty)
            ].get("score"):
                all_scores[mcode, difficulty] = {
                    "game_version": game_version,
                    "ddr_id": ddr_id,
                    "mcode": mcode,
                    "difficulty": difficulty,
                    "rank": record["rank"],
                    "lamp": record["lamp"],
                    "score": score,
                    "exscore": record["exscore"],
                    "ghostid": record.doc_id,
                }
        scores = list(all_scores.values())

    elif loadflag == 4:
        scores = []
        for s in db.table("ddr_scores_best").search(where("ddr_id") == ddrcode):
            scores.append(s)

    names = {}
    rival_records = []

    profiles = db.table("ddr_profile")
    for p in profiles:
        names[p["ddr_id"]] = {}
        try:
            names[p["ddr_id"]]["name"] = p["version"][str(20)]["common_dancername"]
            names[p["ddr_id"]]["area"] = int(p["version"][str(20)]["common_area"])
        except KeyError:
            try:
                names[p["ddr_id"]]["name"] = p["version"][str(19)]["common"].split(",")[27]
                names[p["ddr_id"]]["area"] = int(str(p["version"][str(19)]["common"].split(",")[3]), 16)
            except KeyError:
                names[p["ddr_id"]]["name"] = "UNKNOWN"
                names[p["ddr_id"]]["area"] = 13

    for r in scores:
        diffi = r["difficulty"]
        if diffi > 4:
            style = 1
            diffi -= 4
        else:
            style = 0
        rival_records.append(f"{r["mcode"]},{style},{diffi},0,{names[r["ddr_id"]]["name"] if r["ddr_id"] in names else "UNKNOWN"},0,0,1,{r["score"]},{r["ghostid"]}")

    response = E.response(
        E.playdata_3(
            E.result(0, __type="s32"),
            *[
                E.record(
                    E.record_str(s, __type="str")    
                )
            for s in rival_records
            ]
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/playdata_3/playerdata_new")
async def playdata_3_playerdata_new(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    data = request_info["root"][0].find("data")
    refid = data.find("refid").text

    db = get_db()
    all_profiles_for_card = db.table("ddr_profile").get(Query().card == refid)
    if "ddr_id" not in all_profiles_for_card:
        ddr_id = random.randint(10000000, 99999999)
        all_profiles_for_card["ddr_id"] = ddr_id
    else:
        ddr_id = all_profiles_for_card["ddr_id"]
    tmp = {"game_version": game_version}
    for k in load_settings:
        for v in load_settings[k]:
            tmp[f"{k}_" + v] = 0
    tmp["rival_1_ddr_id"] = 0
    tmp["rival_2_ddr_id"] = 0
    tmp["rival_3_ddr_id"] = 0
    tmp["customize"] = customize_settings
    all_profiles_for_card["version"][str(game_version)] = tmp

    db.table("ddr_profile").upsert(all_profiles_for_card, where("card") == refid)


    response = E.response(
        E.playdata_3(
            E.result(0, __type="s32"),
            E.refid(refid, __type="str"),
            E.ddrcode(ddr_id, __type="s32"),
            E.istakeover(0, __type="bool"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/playdata_3/playerdata_save")
async def playdata_3_playerdata_save(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    retrycnt = int(request_info["root"][0].find("retrycnt").text)
    data = request_info["root"][0].find("data")

    refid = data.find("refid").text
    savekind = int(data.find("savekind").text)

    profile = get_profile(refid)
    game_profile = get_game_profile(refid, game_version)

    db = get_db()

    if not refid.startswith("X000"):
        if savekind in (1, 3):
            for k in load_settings:
                for v in load_settings[k]:
                    profile_setting = data.find(k).find(v)
                    if v == "playcount":
                        game_profile["common_playcount"] += 1
                    elif v.startswith("popup_subscribe"):
                        game_profile["common_" + v] = "0"
                    elif profile_setting is not None:
                        game_profile[f"{k}_" + v] = profile_setting.text
            if "customize" not in game_profile:
                game_profile["customize"] = customize_settings
            profile["version"][str(game_version)] = game_profile
            get_db().table("ddr_profile").upsert(profile, where("card") == refid)

        elif savekind == 2 and retrycnt == 0:
            timestamp = time.time()

            ddr_id = int(data.find("common").find("ddrcode").text)
            pcbid = data.find("pcbid").text
            shoparea = data.find("region").text

            n = data.find("result")

            playstyle = int(n.find("style").text)
            mcode = int(n.find("mcode").text)
            diffi = int(n.find("difficulty").text)
            difficulty = diffi + 4 if playstyle == 1 else diffi
            rank = int(n.find("rank").text)
            lamp = int(n.find("clearkind").text)
            score = int(n.find("score").text)
            exscore = int(n.find("exscore").text)
            maxcombo = int(n.find("maxcombo").text)
            #life = int(n.find("life").text)
            fastcount = int(n.find("fastcount").text)
            slowcount = int(n.find("slowcount").text)
            judge_marvelous = int(n.find("judge_marv").text)
            judge_perfect = int(n.find("judge_perf").text)
            judge_great = int(n.find("judge_great").text)
            judge_good = int(n.find("judge_good").text)
            #judge_boo = int(n.find("judge_boo").text)
            judge_miss = int(n.find("judge_miss").text)
            judge_ok = int(n.find("judge_ok").text)
            judge_ng = int(n.find("judge_ng").text)
            calorie = int(n.find("calorie").text)
            ghostsize = int(n.find("ghostsize").text)
            ghost = n.find("ghost").text
            flare_force = int(n.find("flare_force").text)

            db.table("ddr_scores").insert(
                {
                    "timestamp": timestamp,
                    "pcbid": pcbid,
                    "shoparea": shoparea,
                    "game_version": game_version,
                    "ddr_id": ddr_id,
                    "playstyle": playstyle,
                    "mcode": mcode,
                    "difficulty": difficulty,
                    "rank": rank,
                    "lamp": lamp,
                    "score": score,
                    "exscore": exscore,
                    "maxcombo": maxcombo,
                    "life": -1,
                    "fastcount": fastcount,
                    "slowcount": slowcount,
                    "judge_marvelous": judge_marvelous,
                    "judge_perfect": judge_perfect,
                    "judge_great": judge_great,
                    "judge_good": judge_good,
                    "judge_boo": 0,
                    "judge_miss": judge_miss,
                    "judge_ok": judge_ok,
                    "judge_ng": judge_ng,
                    "calorie": calorie,
                    "ghostsize": ghostsize,
                    "ghost": ghost,
                    "flare_force": flare_force,
                },
            )

            best = db.table("ddr_scores_best").get(
                (where("ddr_id") == ddr_id)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
            )
            best = {} if best is None else best

            best_score_data = {
                "game_version": game_version,
                "ddr_id": ddr_id,
                "playstyle": playstyle,
                "mcode": mcode,
                "difficulty": difficulty,
                "rank": min(rank, best.get("rank", rank)),
                "lamp": max(lamp, best.get("lamp", lamp)),
                "score": max(score, best.get("score", score)),
                "exscore": max(exscore, best.get("exscore", exscore)),
                "flare_force": max(flare_force, best.get("flare_force", flare_force)),
            }

            ghostid = db.table("ddr_scores").get(
                (where("ddr_id") == ddr_id)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
                & (where("score") == max(score, best.get("score", score)))
            )
            if ghostid != None:
                best_score_data["ghostid"] = ghostid.doc_id
            else:
                best_score_data["ghostid"] = -1

            db.table("ddr_scores_best").upsert(
                best_score_data,
                (where("ddr_id") == ddr_id)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty),
            )

        response = E.response(
            E.playdata_3(
                E.result(0, __type="s32"),
            )
        )

    else:
        response = E.response(
            E.playdata_3(
                E.result(1, __type="s32"),
            )
        )


    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/playdata_3/ghostdata_load")
async def playdata_3_ghostdata_load(request: Request):
    request_info = await core_process_request(request)

    data = request_info["root"][0].find("data")
    ghostid = int(data.find("ghostid").text)

    record = get_db().table("ddr_scores").get(doc_id=ghostid)

    response = E.response(
        E.playdata_3(
            E.result(0, __type="s32"),
            E.ghostsize(record["ghostsize"], __type="s32"),
            E.ghost(record["ghost"], __type="str"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/playdata_3/mergeddata_load")
async def playdata_3_mergeddata_load(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.playdata_3(
            E.result(0, __type="s32"),
            E.league_class(0, __type="s32"),
            E.is_advance_border_exceeded(0, __type="bool"),
            E.is_exists_subscribed_user(0, __type="bool"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
