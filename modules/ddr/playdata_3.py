import random
import time

from tinydb import Query, where

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

from base64 import b64decode, b64encode

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["MDX"]


def get_profile(cid):
    return get_db().table("ddr_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)

common = [
    "dancername",
    "area",
    "extrastar",
    "playcount",
    "today_cal",
    "is_subscribed",
    "popup_subscribe_enable",
    "popup_subscribe_disable",
]

option = [
    "hispeed",
    "gauge",
    "fastslow",
    "guideline",
    "stepzone",
    "timing_disp",
    "visibility",
    "visible_time",
    "lane",
    "lane_hiddenpos",
    "lane_suddenpos",
    "lane_hidsudpos",
    "lane_filter",
    "scroll_direction",
    "scroll_moving",
    "arrow_priority",
    "arrow_placement",
    "arrow_color",
    "arrow_design",
    "cut_timing",
    "cut_freeze",
    "cut_jump",
    "speed_type",
    "real_speed",
    "lane_preview",
    "combo_priority",
    "judge_priority",
    "judge_position",
]

lastplay = [
    "mode",
    "folder",
    "mcode",
    "style",
    "difficulty",
    "window_main",
    "window_sub",
    "target",
    "tab_main",
    "tab_sub",
    "tab_main_graph_type",
    "tab_main_graph_disp",
    "tab_sub_graph_type",
    "tab_sub_graph_disp",
]

filtersort = [
    "title",
    "version",
    "genre",
    "bpm",
    "event",
    "level",
    "flare_rank",
    "clear_rank",
    "flare_skill_target",
    "rival_flare_skill",
    "rival_score_rank",
    "sort_type",
    "order_type",
    "is_quickmode",
    "cleartype",
    "difficulty",
]

checkguide = [
    "tips_basic",
    "tips_option",
    "tips_event",
    "tips_gimmick",
    "tips_advance",
    "guide_scene",
]

brave = [
    "last_braveid",
    "last_window_btn",
]


@router.post("/{gameinfo}/playdata_3/musicdata_load")
async def playdata_3_musicdata_load(request: Request):
    request_info = await core_process_request(request)

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

    if refid != default:
        p = get_profile(refid)
        all_scores = {}
        if p is not None:
            ddr_id = p["ddr_id"]
            profile = get_game_profile(refid, game_version)

            for record in get_db().table("ddr_scores_best").search(where("ddr_id") == ddr_id):
                mcode = record["mcode"]
                difficulty = record["difficulty"]
                if mcode not in all_scores:
                    all_scores[mcode] = {}
                if difficulty > 4:
                    all_scores[mcode][difficulty] = f"{int(difficulty) - 4},1,{record["rank"]},{record["lamp"]},{record["score"]},{record["ghostid"]},0,0,0"
                else:
                    all_scores[mcode][difficulty] = f"{difficulty},1,{record["rank"]},{record["lamp"]},{record["score"]},{record["ghostid"]},0,0,0"


    else:
        profile = None

    if profile == None:
        response = E.response(
            E.playdata_3(
                E.result(0, __type="s32"),
                E.refid(refid, __type="str"),
                E.gamesession(1, __type="s64"),
                E.servertime(round(time.time() * 1000), __type="u64"),
                E.is_locked(0, __type="bool"),
                E.common(
                    E.ddrcode(0, __type="s32"),
                    E.dancername("", __type="str"),
                    E.is_new(1, __type="bool"),
                    E.is_registering(0, __type="bool"),
                    E.area(0, __type="s32"),
                    E.extrastar(0, __type="s32"),
                    E.playcount(0, __type="s32"),
                    E.weight(0, __type="s32"),
                    E.today_cal(0, __type="u64"),
                    E.is_disp_weight(0, __type="bool"),
                    E.is_takeover(0, __type="bool"),
                    E.pre_playable_num(0, __type="s32"),
                    E.is_subscribed(0, __type="bool"),
                    E.popup_subscribe_enable(0, __type="bool"),
                    E.popup_subscribe_disable(0, __type="bool"),
                ),
                E.option(
                    E.hispeed(0, __type="s32"),
                    E.gauge(0, __type="s32"),
                    E.fastslow(0, __type="s32"),
                    E.guideline(0, __type="s32"),
                    E.stepzone(0, __type="s32"),
                    E.timing_disp(0, __type="s32"),
                    E.visibility(0, __type="s32"),
                    E.visible_time(0, __type="s32"),
                    E.lane(0, __type="s32"),
                    E.lane_hiddenpos(0, __type="s32"),
                    E.lane_suddenpos(0, __type="s32"),
                    E.lane_hidsudpos(0, __type="s32"),
                    E.lane_filter(0, __type="s32"),
                    E.scroll_direction(0, __type="s32"),
                    E.scroll_moving(0, __type="s32"),
                    E.arrow_priority(0, __type="s32"),
                    E.arrow_placement(0, __type="s32"),
                    E.arrow_color(0, __type="s32"),
                    E.arrow_design(0, __type="s32"),
                    E.cut_timing(0, __type="s32"),
                    E.cut_freeze(0, __type="s32"),
                    E.cut_jump(0, __type="s32"),
                    E.speed_type(0, __type="s32"),
                    E.real_speed(0, __type="s32"),
                    E.lane_preview(0, __type="s32"),
                    E.combo_priority(0, __type="s32"),
                    E.judge_priority(0, __type="s32"),
                    E.judge_position(0, __type="s32"),
                ),
                E.lastplay(
                    E.mode(0, __type="s32"),
                    E.folder(0, __type="s32"),
                    E.mcode(0, __type="s32"),
                    E.style(0, __type="s32"),
                    E.difficulty(0, __type="s32"),
                    E.window_main(0, __type="s32"),
                    E.window_sub(0, __type="s32"),
                    E.target(0, __type="s32"),
                    E.tab_main(0, __type="s32"),
                    E.tab_sub(0, __type="s32"),
                    E.tab_main_graph_type(0, __type="s32"),
                    E.tab_main_graph_disp(0, __type="s32"),
                    E.tab_sub_graph_type(0, __type="s32"),
                    E.tab_sub_graph_disp(0, __type="s32"),
                ),
                E.filtersort(
                    E.title(0, __type="u64"),
                    E.version(0, __type="u64"),
                    E.genre(0, __type="u64"),
                    E.bpm(0, __type="u64"),
                    E.event(0, __type="u64"),
                    E.level(0, __type="u64"),
                    E.flare_rank(0, __type="u64"),
                    E.clear_rank(0, __type="u64"),
                    E.flare_skill_target(0, __type="u64"),
                    E.rival_flare_skill(0, __type="u64"),
                    E.rival_score_rank(0, __type="u64"),
                    E.sort_type(0, __type="u64"),
                    E.order_type(0, __type="s32"),
                    E.is_quickmode(0, __type="bool"),
                    E.cleartype(0, __type="u64"),
                    E.difficulty(0, __type="u64"),
                ),
                E.checkguide(
                    E.tips_basic(0, __type="u64"),
                    E.tips_option(0, __type="u64"),
                    E.tips_event(0, __type="u64"),
                    E.tips_gimmick(0, __type="u64"),
                    E.tips_advance(0, __type="u64"),
                    E.guide_scene(0, __type="u64"),
                ),
                E.rival(
                    E.slot(1, __type="s32"),
                    E.rivalcode(0, __type="s32"),
                ),
                E.rival(
                    E.slot(2, __type="s32"),
                    E.rivalcode(0, __type="s32"),
                ),
                E.rival(
                    E.slot(3, __type="s32"),
                    E.rivalcode(0, __type="s32"),
                ),
                E.score(
                    E.mcode(0, __type="s32"),
                    E.score_single(
                        E.score_str("", __type="str"),
                    ),
                    E.score_double(
                        E.score_str("", __type="str"),
                    ),
                ),
                E.event(
                    E.event_str("1,101,0,0,14,0,0", __type="str"),
                ),
                #E.league(),
                #E.current(),
                #E.result(),
                #E.customize(),
                #E.brave(),
            )
        )
    else:
        response = E.response(
            E.playdata_3(
                E.result(0, __type="s32"),
                E.refid(refid, __type="str"),
                E.gamesession(1, __type="s64"),
                E.servertime(round(time.time() * 1000), __type="u64"),
                E.is_locked(0, __type="bool"),
                E.common(
                    E.ddrcode(p["ddr_id"], __type="s32"),
                    E.dancername(profile["common_dancername"], __type="str"),
                    E.is_new(0, __type="bool"),
                    E.is_registering(0, __type="bool"),
                    E.area(profile["common_area"], __type="s32"),
                    E.extrastar(profile["common_extrastar"], __type="s32"),
                    E.playcount(profile["common_playcount"], __type="s32"),
                    E.weight(0, __type="s32"),
                    E.today_cal(profile["common_today_cal"], __type="u64"),
                    E.is_disp_weight(0, __type="bool"),
                    E.is_takeover(0, __type="bool"),
                    E.pre_playable_num(1, __type="s32"),
                    E.is_subscribed(1, __type="bool"),
                    E.popup_subscribe_enable(0, __type="bool"),
                    E.popup_subscribe_disable(0, __type="bool"),
                ),
                E.option(
                    E.hispeed(profile["option_hispeed"], __type="s32"),
                    E.gauge(profile["option_gauge"], __type="s32"),
                    E.fastslow(profile["option_fastslow"], __type="s32"),
                    E.guideline(profile["option_guideline"], __type="s32"),
                    E.stepzone(profile["option_stepzone"], __type="s32"),
                    E.timing_disp(profile["option_timing_disp"], __type="s32"),
                    E.visibility(profile["option_visibility"], __type="s32"),
                    E.visible_time(profile["option_visible_time"], __type="s32"),
                    E.lane(profile["option_lane"], __type="s32"),
                    E.lane_hiddenpos(profile["option_lane_hiddenpos"], __type="s32"),
                    E.lane_suddenpos(profile["option_lane_suddenpos"], __type="s32"),
                    E.lane_hidsudpos(profile["option_lane_hidsudpos"], __type="s32"),
                    E.lane_filter(profile["option_lane_filter"], __type="s32"),
                    E.scroll_direction(profile["option_scroll_direction"], __type="s32"),
                    E.scroll_moving(profile["option_scroll_moving"], __type="s32"),
                    E.arrow_priority(profile["option_arrow_priority"], __type="s32"),
                    E.arrow_placement(profile["option_arrow_placement"], __type="s32"),
                    E.arrow_color(profile["option_arrow_color"], __type="s32"),
                    E.arrow_design(profile["option_arrow_design"], __type="s32"),
                    E.cut_timing(profile["option_cut_timing"], __type="s32"),
                    E.cut_freeze(profile["option_cut_freeze"], __type="s32"),
                    E.cut_jump(profile["option_cut_jump"], __type="s32"),
                    E.speed_type(profile["option_speed_type"], __type="s32"),
                    E.real_speed(profile["option_real_speed"], __type="s32"),
                    E.lane_preview(profile["option_lane_preview"], __type="s32"),
                    E.combo_priority(profile["option_combo_priority"], __type="s32"),
                    E.judge_priority(profile["option_judge_priority"], __type="s32"),
                    E.judge_position(profile["option_judge_position"], __type="s32"),
                ),
                E.lastplay(
                    E.mode(profile["lastplay_mode"], __type="s32"),
                    E.folder(profile["lastplay_folder"], __type="s32"),
                    E.mcode(profile["lastplay_mcode"], __type="s32"),
                    E.style(profile["lastplay_style"], __type="s32"),
                    E.difficulty(profile["lastplay_difficulty"], __type="s32"),
                    E.window_main(profile["lastplay_window_main"], __type="s32"),
                    E.window_sub(profile["lastplay_window_sub"], __type="s32"),
                    E.target(profile["lastplay_target"], __type="s32"),
                    E.tab_main(profile["lastplay_tab_main"], __type="s32"),
                    E.tab_sub(profile["lastplay_tab_sub"], __type="s32"),
                    E.tab_main_graph_type(profile["lastplay_tab_main_graph_type"], __type="s32"),
                    E.tab_main_graph_disp(profile["lastplay_tab_main_graph_disp"], __type="s32"),
                    E.tab_sub_graph_type(profile["lastplay_tab_sub_graph_type"], __type="s32"),
                    E.tab_sub_graph_disp(profile["lastplay_tab_sub_graph_disp"], __type="s32"),
                ),
                E.filtersort(
                    E.title(profile["filtersort_title"], __type="u64"),
                    E.version(profile["filtersort_version"], __type="u64"),
                    E.genre(profile["filtersort_genre"], __type="u64"),
                    E.bpm(profile["filtersort_bpm"], __type="u64"),
                    E.event(profile["filtersort_event"], __type="u64"),
                    E.level(profile["filtersort_level"], __type="u64"),
                    E.flare_rank(profile["filtersort_flare_rank"], __type="u64"),
                    E.clear_rank(profile["filtersort_clear_rank"], __type="u64"),
                    E.flare_skill_target(profile["filtersort_flare_skill_target"], __type="u64"),
                    E.rival_flare_skill(profile["filtersort_rival_flare_skill"], __type="u64"),
                    E.rival_score_rank(profile["filtersort_rival_score_rank"], __type="u64"),
                    E.sort_type(profile["filtersort_sort_type"], __type="u64"),
                    E.order_type(profile["filtersort_order_type"], __type="s32"),
                    E.is_quickmode(profile["filtersort_is_quickmode"], __type="bool"),
                    E.cleartype(profile["filtersort_cleartype"], __type="u64"),
                    E.difficulty(profile["filtersort_difficulty"], __type="u64"),
                ),
                E.checkguide(
                    E.tips_basic(profile["checkguide_tips_basic"], __type="u64"),
                    E.tips_option(profile["checkguide_tips_option"], __type="u64"),
                    E.tips_event(profile["checkguide_tips_event"], __type="u64"),
                    E.tips_gimmick(profile["checkguide_tips_gimmick"], __type="u64"),
                    E.tips_advance(profile["checkguide_tips_advance"], __type="u64"),
                    E.guide_scene(profile["checkguide_guide_scene"], __type="u64"),
                ),
                E.rival(
                    E.slot(1, __type="s32"),
                    E.rivalcode(profile.get("rival_1_ddr_id", 0), __type="s32"),
                ),
                E.rival(
                    E.slot(2, __type="s32"),
                    E.rivalcode(profile.get("rival_2_ddr_id", 0), __type="s32"),
                ),
                E.rival(
                    E.slot(3, __type="s32"),
                    E.rivalcode(profile.get("rival_3_ddr_id", 0), __type="s32"),
                ),
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
                #E.result(),
                #appeal_board
                E.customize(
                    E.category(1, __type="s32"),
                    E.key(100006, __type="s32"),
                    E.pattern(0, __type="s32"),
                ),
                #character_left
                E.customize(
                    E.category(2, __type="s32"),
                    E.key(4, __type="s32"),
                    E.pattern(1, __type="s32"),
                ),
                #character_right
                E.customize(
                    E.category(2, __type="s32"),
                    E.key(1, __type="s32"),
                    E.pattern(2, __type="s32"),
                ),
                ##game_bg_system
                #E.customize(
                #    E.category(3, __type="s32"),
                #    E.key(2, __type="s32"),
                #    E.pattern(1, __type="s32"),
                #),
                ##game_bg_play
                #E.customize(
                #    E.category(3, __type="s32"),
                #    E.key(24, __type="s32"),
                #    E.pattern(2, __type="s32"),
                #),
                ##lane_bg_single
                #E.customize(
                #    E.category(4, __type="s32"),
                #    E.key(20, __type="s32"),
                #    E.pattern(0, __type="s32"),
                #),
                ##lane_bg_double
                #E.customize(
                #    E.category(5, __type="s32"),
                #    E.key(20, __type="s32"),
                #    E.pattern(0, __type="s32"),
                #),
                ##lane_cover_single
                #E.customize(
                #    E.category(6, __type="s32"),
                #    E.key(1, __type="s32"),
                #    E.pattern(0, __type="s32"),
                #),
                ##lane_cover_double
                #E.customize(
                #    E.category(7, __type="s32"),
                #    E.key(1, __type="s32"),
                #    E.pattern(0, __type="s32"),
                #),
                #song_vid
                E.customize(
                    E.category(8, __type="s32"),
                    E.key(2, __type="s32"),
                    E.pattern(0, __type="s32"),
                ),
                #E.brave(),
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

    load = []
    names = {}

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
        load.append(f"{r["mcode"]},{style},{diffi},0,{names[r["ddr_id"]]["name"] if r["ddr_id"] in names else "UNKNOWN"},0,0,1,{r["score"]},{r["ghostid"]}")

    response = E.response(
        E.playdata_3(
            E.result(0, __type="s32"),
            *[
                E.record(
                    E.record_str(s, __type="str")    
                )
            for s in load
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
    for k in common:
        tmp["common_" + k] = 0
    for k in option:
        tmp["option_" + k] = 0
    for k in lastplay:
        tmp["lastplay_" + k] = 0
    for k in filtersort:
        tmp["filtersort_" + k] = 0
    for k in checkguide:
        tmp["checkguide_" + k] = 0
    for k in brave:
        tmp["brave_" + k] = 0
    tmp["rival_1_ddr_id"] = 0
    tmp["rival_2_ddr_id"] = 0
    tmp["rival_3_ddr_id"] = 0
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

    data = request_info["root"][0].find("data")

    refid = data.find("refid").text
    savekind = int(data.find("savekind").text)

    profile = get_profile(refid)
    game_profile = get_game_profile(refid, game_version)

    db = get_db()

    if not refid.startswith("X000"):
        if savekind in (1, 3):
            for k in common:
                if k == "playcount":
                    game_profile["common_playcount"] += 1
                elif k.startswith("popup_subscribe"):
                    game_profile["common_" + k] = "0"
                else:
                    game_profile["common_" + k] = data.find("common").find(k).text
            for k in option:
                game_profile["option_" + k] = data.find("option").find(k).text
            for k in lastplay:
                game_profile["lastplay_" + k] = data.find("lastplay").find(k).text
            for k in filtersort:
                game_profile["filtersort_" + k] = data.find("filtersort").find(k).text
            for k in checkguide:
                game_profile["checkguide_" + k] = data.find("checkguide").find(k).text
            for k in brave:
                game_profile["brave_" + k] = data.find("brave").find(k).text
            profile["version"][str(game_version)] = game_profile
            get_db().table("ddr_profile").upsert(profile, where("card") == refid)

        elif savekind == 2:
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
            }

            ghostid = db.table("ddr_scores").get(
                (where("ddr_id") == ddr_id)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
                & (where("score") == max(score, best.get("score", score)))
            )
            best_score_data["ghostid"] = ghostid.doc_id

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

