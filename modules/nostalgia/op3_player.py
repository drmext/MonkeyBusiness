from tinydb import Query, where

import random

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["PAN"]


def get_profile(cid):
    return get_db().table("nostalgia_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


@router.post("/{gameinfo}/op3_player/regist_playdata")
async def op3_player_regist_playdata(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0]

    dataid = root.find("dataid").text
    refid = root.find("refid").text
    name = root.find("name").text

    db = get_db().table("nostalgia_profile")
    all_profiles_for_card = db.get(Query().card == dataid)

    if all_profiles_for_card is None:
        all_profiles_for_card = {"card": dataid, "version": {}}

    if "nostalgia_id" not in all_profiles_for_card:
        nostalgia_id = random.randint(10000000, 99999999)
        all_profiles_for_card["nostalgia_id"] = nostalgia_id

    all_profiles_for_card["version"][str(game_version)] = {
        "game_version": game_version,
        "name": name,
        "music_group": 0,
        "music_index": 0,
        "sheet_type": 0,
        "perform_type": 0,
        "filter_flag": 0,
        "brooch_index": 0,
        "hi_speed_level": 0,
        "beat_guide": 0,
        "headphone_volume": 0,
        "judge_bar_pos": 250,
        "hands_mode": 0,
        "near_setting": 0,
        "judge_delay_offset": 0,
        "key_beam_level": 0,
        "orbit_type": 0,
        "note_height": 10,
        "note_width": 10,
        "judge_width_type": 10,
        "beat_guide_volume": 0,
        "beat_guide_type": 0,
        "key_volume_offset": 0,
        "bgm_volume_offset": 0,
        "note_disp_type": 0,
        "slow_fast": 0,
        "option_setting": 0,
        "judge_effect_adjust": 0,
        "simple_bg": 0,
        "bingo_index": 0,
        "class_basic": 0,
        "class_recital": 0,
        "grade_basic": 0,
        "grade_recital": 0,
        "money": 0,
        "pianist_power": 0,
        "fame_index": 0,
        "kingdom_id": 0,
        "quest_index": 0,
        "param1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "param2": [0, 0, 0, 0, 0, 0, 0, 0],
    }

    db.upsert(all_profiles_for_card, where("card") == dataid)

    response = E.response(
        E.regist_playdata(
            E.permitted_list(
                E.flag([-1] * 32, __type="s32", sheet_type="0"),
                E.flag([-1] * 32, __type="s32", sheet_type="1"),
                E.flag([-1] * 32, __type="s32", sheet_type="2"),
                E.flag([-1] * 32, __type="s32", sheet_type="3"),
            ),
            E.valid_quest_list(E.quest(index="1")),
            E.valid_course_list(E.course(index="1")),
            E.name(name, __type="str"),
            E.play_count(0, __type="s32"),
            E.today_play_count(0, __type="s32"),
            E.old_play_count(0, __type="s32"),
            E.old_recital_count(0, __type="s32"),
            E.music_list(
                E.flag([-1] * 32, __type="s32", sheet_type="0"),
                E.flag([-1] * 32, __type="s32", sheet_type="1"),
                E.flag([-1] * 32, __type="s32", sheet_type="2"),
                E.flag([-1] * 32, __type="s32", sheet_type="3"),
            ),
            E.free_for_play_music_list(
                E.flag([-1] * 32, __type="s32", sheet_type="0"),
                E.flag([-1] * 32, __type="s32", sheet_type="1"),
                E.flag([-1] * 32, __type="s32", sheet_type="2"),
                E.flag([-1] * 32, __type="s32", sheet_type="3"),
            ),
            E.last(
                E.music_group(0, __type="s32"),
                E.music_index(0, __type="s32"),
                E.sheet_type(0, __type="s8"),
                E.perform_type(0, __type="s32"),
                E.filter_flag(0, __type="u64"),
                E.brooch_index(0, __type="s32"),
                E.hi_speed_level(0, __type="s32"),
                E.beat_guide(0, __type="s8"),
                E.headphone_volume(0, __type="s8"),
                E.judge_bar_pos(0, __type="s32"),
                E.hands_mode(0, __type="s8"),
                E.near_setting(0, __type="s8"),
                E.judge_delay_offset(0, __type="s8"),
                E.key_beam_level(0, __type="s8"),
                E.orbit_type(0, __type="s8"),
                E.note_height(0, __type="s8"),
                E.note_width(0, __type="s8"),
                E.judge_width_type(0, __type="s8"),
                E.beat_guide_volume(0, __type="s8"),
                E.beat_guide_type(0, __type="s8"),
                E.key_volume_offset(0, __type="s8"),
                E.bgm_volume_offset(0, __type="s8"),
                E.note_disp_type(0, __type="s8"),
                E.slow_fast(0, __type="s8"),
                E.option_setting(0, __type="s32"),
                E.judge_effect_adjust(0, __type="s8"),
                E.simple_bg(0, __type="s8"),
                E.bingo_index(0, __type="s32"),
            ),
            E.travel(
                E.money(0, __type="s32"),
                E.pianist_power(0, __type="s32"),
                E.fame_index(0, __type="s32"),
                E.kingdom_id(0, __type="s32"),
                E.quest_index(0, __type="s32"),
            ),
            # E.brooch_list(),
            # E.enquete_list(),
            # E.event_list(),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/op3_player/get_musicdata")
async def op3_player_get_musicdata(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    refid = request_info["root"][0].find("refid").text
    profile = get_game_profile(refid, game_version)
    nostalgia_id = get_profile(refid)["nostalgia_id"]

    records = (
        get_db()
        .table("nostalgia_scores_best")
        .search(where("nostalgia_id") == nostalgia_id)
    )

    response = E.response(
        E.get_musicdata(
            *[
                E.music(
                    E.recital(
                        E.score(r["score"], __type="s32"),
                        E.play_count(r["play_count"], __type="s32"),
                        E.clear_count(r["clear_count"], __type="s32"),
                        E.multi_count(r["multi_count"], __type="s32"),
                        E.clear_flag(r["clear_flag"], __type="s32"),
                        E.hands_mode(r["hands_mode"], __type="s8"),
                        E.evaluation(5, __type="u32"),
                        E.grade(r["grade"], __type="u32"),
                    ),
                    E.score(r["score"], __type="s32"),
                    E.play_count(r["play_count"], __type="s32"),
                    E.clear_count(r["clear_count"], __type="s32"),
                    E.multi_count(r["multi_count"], __type="s32"),
                    E.clear_flag(r["clear_flag"], __type="s32"),
                    E.hands_mode(r["hands_mode"], __type="s8"),
                    E.evaluation(5, __type="u32"),
                    E.grade(r["grade"], __type="u32"),
                    sheet_type=r["sheet_type"],
                    music_index=r["music_index"],
                )
                for r in records
            ],
            # E.new_music_list(
            #    *[E.music(
            #        E.unlock_time(0, __type="u64"),
            #        sheet_type="2",
            #        music_index=x
            #    )for x in range(1,300)],
            # ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/op3_player/get_playdata")
async def op3_player_get_playdata(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    refid = request_info["root"][0].find("refid").text
    profile = get_game_profile(refid, game_version)

    response = E.response(
        E.get_playdata(
            E.permitted_list(
                E.flag([-1] * 32, __type="s32", sheet_type="0"),
                E.flag([-1] * 32, __type="s32", sheet_type="1"),
                E.flag([-1] * 32, __type="s32", sheet_type="2"),
                E.flag([-1] * 32, __type="s32", sheet_type="3"),
            ),
            # E.valid_quest_list(
            #    E.quest(index="1")
            # ),
            # E.valid_course_list(
            #    E.course(index="1")
            # ),
            E.name(profile["name"], __type="str"),
            E.play_count(0, __type="s32"),
            E.today_play_count(0, __type="s32"),
            E.old_play_count(0, __type="s32"),
            E.old_recital_count(0, __type="s32"),
            E.music_list(
                E.flag([-1] * 32, __type="s32", sheet_type="0"),
                E.flag([-1] * 32, __type="s32", sheet_type="1"),
                E.flag([-1] * 32, __type="s32", sheet_type="2"),
                E.flag([-1] * 32, __type="s32", sheet_type="3"),
            ),
            E.free_for_play_music_list(
                E.flag([-1] * 32, __type="s32", sheet_type="0"),
                E.flag([-1] * 32, __type="s32", sheet_type="1"),
                E.flag([-1] * 32, __type="s32", sheet_type="2"),
                E.flag([-1] * 32, __type="s32", sheet_type="3"),
            ),
            E.last(
                E.music_group(profile["music_group"], __type="s32"),
                E.music_index(profile["music_index"], __type="s32"),
                E.sheet_type(profile["sheet_type"], __type="s8"),
                E.perform_type(profile["perform_type"], __type="s32"),
                E.filter_flag(profile["filter_flag"], __type="u64"),
                E.brooch_index(profile["brooch_index"], __type="s32"),
                E.hi_speed_level(profile["hi_speed_level"], __type="s32"),
                E.beat_guide(profile["beat_guide"], __type="s8"),
                E.headphone_volume(profile["headphone_volume"], __type="s8"),
                E.judge_bar_pos(profile["judge_bar_pos"], __type="s32"),
                E.hands_mode(profile["hands_mode"], __type="s8"),
                E.near_setting(profile["near_setting"], __type="s8"),
                E.judge_delay_offset(profile["judge_delay_offset"], __type="s8"),
                E.key_beam_level(profile["key_beam_level"], __type="s8"),
                E.orbit_type(profile["orbit_type"], __type="s8"),
                E.note_height(profile["note_height"], __type="s8"),
                E.note_width(profile["note_width"], __type="s8"),
                E.judge_width_type(profile["judge_width_type"], __type="s8"),
                E.beat_guide_volume(profile["beat_guide_volume"], __type="s8"),
                E.beat_guide_type(profile["beat_guide_type"], __type="s8"),
                E.key_volume_offset(profile["key_volume_offset"], __type="s8"),
                E.bgm_volume_offset(profile["bgm_volume_offset"], __type="s8"),
                E.note_disp_type(profile["note_disp_type"], __type="s8"),
                E.slow_fast(profile["slow_fast"], __type="s8"),
                E.option_setting(profile["option_setting"], __type="s32"),
                E.judge_effect_adjust(profile["judge_effect_adjust"], __type="s8"),
                E.simple_bg(profile["simple_bg"], __type="s8"),
                E.bingo_index(profile["bingo_index"], __type="s32"),
                E.class_basic(profile["class_basic"], __type="s32"),
                E.class_recital(profile["class_recital"], __type="s32"),
                E.grade_basic(profile["grade_basic"], __type="s32"),
                E.grade_recital(profile["grade_recital"], __type="s32"),
            ),
            E.travel(
                E.money(profile["money"], __type="s32"),
                E.pianist_power(profile["pianist_power"], __type="s32"),
                E.fame_index(profile["fame_index"], __type="s32"),
                E.kingdom_id(profile["kingdom_id"], __type="s32"),
                E.quest_index(profile["quest_index"], __type="s32"),
            ),
            E.extra_param(
                E.param(
                    E.count(len(profile["param1"]), __type="s32"),
                    E.params_array(profile["param1"], __type="s32"),
                    type="1",
                ),
                E.param(
                    E.count(len(profile["param2"]), __type="s32"),
                    E.params_array(profile["param2"], __type="s32"),
                    type="2",
                ),
                # E.param(
                #    E.count(11, __type="s32"),
                #    E.params_array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], __type="s32"),
                #    type="1"
                # ),
                # E.param(
                #    E.count(8, __type="s32"),
                #    E.params_array([64, 0, 0, 0, 0, 0, 0, 0], __type="s32"),
                #    type="2"
                # ),
            ),
            # E.brooch_list(),
            # E.enquete_list(),
            # E.event_list(),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/op3_player/set_stage_result")
async def op3_player_set_stage_result(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0]

    refid = root.find("refid").text
    profile = get_profile(refid)
    nostalgia_id = profile["nostalgia_id"]
    game_profile = profile["version"].get(str(game_version), {})

    stageinfo = root.find("stageinfo")

    stages = stageinfo.findall("stage")
    stage = stages[-1]
    common = stage.find("common")

    music_index = int(stage.get("music_index"))
    sheet_type = int(stage.get("sheet_type"))
    play_time = int(common.find("play_time").text)
    score = int(common.find("score").text)
    combo = int(common.find("combo").text)
    grade = int(common.find("grade").text)
    hands_mode = int(common.find("hands_mode").text)
    play_count = int(common.find("play_count").text)
    clear_count = int(common.find("clear_count").text)
    multi_count = int(common.find("multi_count").text)
    clear_flag = int(common.find("clear_flag").text)
    slow_count = int(common.find("slow_count").text)
    fast_count = int(common.find("fast_count").text)
    judge_count_miss = int(common.find("judge_count/miss").text)
    judge_count_good = int(common.find("judge_count/good").text)
    judge_count_just = int(common.find("judge_count/just").text)
    judge_count_super_just = int(common.find("judge_count/super_just").text)
    judge_count_near = int(common.find("judge_count/near").text)
    judge_percent_max_count_long_miss = int(
        common.find("judge_percent_max_count_long/miss").text
    )
    judge_percent_max_count_long_good = int(
        common.find("judge_percent_max_count_long/good").text
    )
    judge_percent_max_count_long_just = int(
        common.find("judge_percent_max_count_long/just").text
    )
    judge_percent_max_count_long_super_just = int(
        common.find("judge_percent_max_count_long/super_just").text
    )
    judge_percent_max_count_long_near = int(
        common.find("judge_percent_max_count_long/near").text
    )
    judge_percent_max_count_trill_miss = int(
        common.find("judge_percent_max_count_trill/miss").text
    )
    judge_percent_max_count_trill_good = int(
        common.find("judge_percent_max_count_trill/good").text
    )
    judge_percent_max_count_trill_just = int(
        common.find("judge_percent_max_count_trill/just").text
    )
    judge_percent_max_count_trill_super_just = int(
        common.find("judge_percent_max_count_trill/super_just").text
    )
    judge_percent_max_count_trill_near = int(
        common.find("judge_percent_max_count_trill/near").text
    )
    note_num_normal = int(common.find("note_num/normal").text)
    note_num_long = int(common.find("note_num/long").text)
    note_num_glissando = int(common.find("note_num/glissando").text)
    note_num_trill = int(common.find("note_num/trill").text)
    note_success_rate_normal = int(common.find("note_success_rate/normal").text)
    note_success_rate_long = int(common.find("note_success_rate/long").text)
    note_success_rate_glissando = int(common.find("note_success_rate/glissando").text)
    note_success_rate_trill = int(common.find("note_success_rate/trill").text)
    best_score = int(common.find("best_score").text)

    db = get_db()
    db.table("nostalgia_scores").insert(
        {
            "timestamp": play_time,
            "game_version": game_version,
            "nostalgia_id": nostalgia_id,
            "music_index": music_index,
            "sheet_type": sheet_type,
            "score": score,
            "combo": combo,
            "grade": grade,
            "hands_mode": hands_mode,
            "play_count": play_count,
            "clear_count": clear_count,
            "multi_count": multi_count,
            "clear_flag": clear_flag,
            "slow_count": slow_count,
            "fast_count": fast_count,
            "judge_count_miss": judge_count_miss,
            "judge_count_good": judge_count_good,
            "judge_count_just": judge_count_just,
            "judge_count_super_just": judge_count_super_just,
            "judge_count_near": judge_count_near,
            "judge_percent_max_count_long_miss": judge_percent_max_count_long_miss,
            "judge_percent_max_count_long_good": judge_percent_max_count_long_good,
            "judge_percent_max_count_long_just": judge_percent_max_count_long_just,
            "judge_percent_max_count_long_super_just": judge_percent_max_count_long_super_just,
            "judge_percent_max_count_long_near": judge_percent_max_count_long_near,
            "judge_percent_max_count_trill_miss": judge_percent_max_count_trill_miss,
            "judge_percent_max_count_trill_good": judge_percent_max_count_trill_good,
            "judge_percent_max_count_trill_just": judge_percent_max_count_trill_just,
            "judge_percent_max_count_trill_super_just": judge_percent_max_count_trill_super_just,
            "judge_percent_max_count_trill_near": judge_percent_max_count_trill_near,
            "note_num_normal": note_num_normal,
            "note_num_long": note_num_long,
            "note_num_glissando": note_num_glissando,
            "note_num_trill": note_num_trill,
            "note_success_rate_normal": note_success_rate_normal,
            "note_success_rate_long": note_success_rate_long,
            "note_success_rate_glissando": note_success_rate_glissando,
            "note_success_rate_trill": note_success_rate_trill,
            "best_score": best_score,
        },
    )

    best = db.table("nostalgia_scores_best").get(
        (where("nostalgia_id") == nostalgia_id)
        & (where("music_index") == music_index)
        & (where("sheet_type") == sheet_type)
    )
    best = {} if best is None else best

    best_score_data = {
        "game_version": game_version,
        "nostalgia_id": nostalgia_id,
        "music_index": music_index,
        "sheet_type": sheet_type,
        "score": max(score, best.get("score", score)),
        "play_count": play_count,
        "clear_count": clear_count,
        "multi_count": multi_count,
        "clear_flag": max(clear_flag, best.get("clear_flag", clear_flag)),
        "hands_mode": max(hands_mode, best.get("hands_mode", hands_mode)),
        "grade": max(grade, best.get("grade", grade)),
    }

    db.table("nostalgia_scores_best").upsert(
        best_score_data,
        (where("nostalgia_id") == nostalgia_id)
        & (where("music_index") == music_index)
        & (where("sheet_type") == sheet_type),
    )

    response = E.response(E.set_stage_result(E.player()))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/op3_player/set_total_result")
async def op3_player_set_total_result(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0]

    refid = root.find("refid").text
    profile = get_profile(refid)
    nostalgia_id = profile["nostalgia_id"]
    game_profile = profile["version"].get(str(game_version), {})

    for k in [
        "music_group",
        "music_index",
        "sheet_type",
        "perform_type",
        "filter_flag",
        "brooch_index",
        "hi_speed_level",
        "beat_guide",
        "headphone_volume",
        "judge_bar_pos",
        "hands_mode",
        "near_setting",
        "judge_delay_offset",
        "key_beam_level",
        "orbit_type",
        "note_height",
        "note_width",
        "judge_width_type",
        "beat_guide_volume",
        "beat_guide_type",
        "key_volume_offset",
        "bgm_volume_offset",
        "note_disp_type",
        "slow_fast",
        "option_setting",
        "judge_effect_adjust",
        "simple_bg",
        "bingo_index",
        "class_basic",
        "class_recital",
        "grade_basic",
        "grade_recital",
    ]:
        game_profile[k] = int(root.find(f"last/{k}").text)

    for k in [
        "money",
        "pianist_power",
        "fame_index",
        "kingdom_id",
        "quest_index",
    ]:
        game_profile[k] = int(root.find(f"travel/{k}").text)

    extra_param = root.find("extra_param")
    params = extra_param.findall("param")
    for param in params:
        game_profile[f"param{param.get('type')}"] = [
            int(x) for x in param.find("params_array").text.split(" ")
        ]

    profile["version"][str(game_version)] = game_profile

    get_db().table("nostalgia_profile").upsert(profile, where("card") == refid)

    response = E.response(E.set_total_result(E.player()))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
