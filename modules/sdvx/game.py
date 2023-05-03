from tinydb import Query, where

import config
import random
import time

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["KFC"]


def get_profile(cid):
    return get_db().table("sdvx_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


def get_id_from_profile(cid):
    profile = get_db().table("sdvx_profile").get(where("card") == cid)

    djid = "%08d" % profile["sdvx_id"]
    djid_split = "-".join([djid[:4], djid[4:]])

    return profile["sdvx_id"], djid_split


@router.post("/{gameinfo}/game/sv6_common")
async def game_sv6_common(request: Request):
    request_info = await core_process_request(request)

    event = [
        "DEMOGAME_PLAY",
        "MATCHING_MODE",
        "MATCHING_MODE_FREE_IP",
        "LEVEL_LIMIT_EASING",
        "ACHIEVEMENT_ENABLE",
        "APICAGACHADRAW\t30",
        "VOLFORCE_ENABLE",
        "AKANAME_ENABLE",
        "PAUSE_ONLINEUPDATE",
        "CONTINUATION",
        "TENKAICHI_MODE",
        "QC_MODE",
        "KAC_MODE",
        # "APPEAL_CARD_GEN_PRICE\t100",
        # "APPEAL_CARD_GEN_NEW_PRICE\t200",
        # "APPEAL_CARD_UNLOCK\t0,20170914,0,20171014,0,20171116,0,20180201,0,20180607,0,20181206,0,20200326,0,20200611,4,10140732,6,10150431",
        "FAVORITE_APPEALCARD_MAX\t200",
        "FAVORITE_MUSIC_MAX\t200",
        "EVENTDATE_APRILFOOL",
        "KONAMI_50TH_LOGO",
        "OMEGA_ARS_ENABLE",
        "DISABLE_MONITOR_ID_CHECK",
        "SKILL_ANALYZER_ABLE",
        "BLASTER_ABLE",
        "STANDARD_UNLOCK_ENABLE",
        "PLAYERJUDGEADJ_ENABLE",
        "MIXID_INPUT_ENABLE",
        "EVENTDATE_ONIGO",
        "EVENTDATE_GOTT",
        "GENERATOR_ABLE",
        "CREW_SELECT_ABLE",
        "PREMIUM_TIME_ENABLE",
        "OMEGA_ENABLE\t1,2,3,4,5,6,7,8,9",
        "HEXA_ENABLE\t1,2,3,4,5,6,7",
        "MEGAMIX_ENABLE",
        "VALGENE_ENABLE",
        "ARENA_ENABLE",
        "ARENA_LOCAL_TO_ONLINE_ENABLE",
        "ARENA_ALTER_MODE_WINDOW_ENABLE",
        "ARENA_PASS_MATCH_WINDOW_ENABLE",
        "DEMOLOOP_PASELI_FESTIVAL_2022",
        "DISABLED_MUSIC_IN_ARENA_ONLINE",
        "ARENA_VOTE_MODE_ENABLE",
        "DISP_PASELI_BANNER",
        "S_PUC_EFFECT_ENABLE",
        "SUPER_RANDOM_ACTIVE",
        "PLAYER_RADAR_ENABLE",
        "SINGLE_BATTLE_ENABLE",
    ]

    unlock = []
    for i in range(3000):
        for j in range(0, 5):
            unlock.append([i, j])

    response = E.response(
        E.game(
            E.event(
                *[
                    E.info(
                        E.event_id(s, __type="str"),
                    )
                    for s in event
                ],
            ),
            E.music_limited(
                *[
                    E.info(
                        E.music_id(s[0], __type="s32"),
                        E.music_type(s[1], __type="u8"),
                        E.limited(3, __type="u8"),
                    )
                    for s in unlock
                ],
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_new")
async def game_sv6_new(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0]

    dataid = root.find("dataid").text
    cardno = root.find("cardno").text
    name = root.find("name").text

    db = get_db().table("sdvx_profile")
    all_profiles_for_card = db.get(Query().card == dataid)

    if all_profiles_for_card is None:
        all_profiles_for_card = {"card": dataid, "version": {}}

    if "sdvx_id" not in all_profiles_for_card:
        sdvx_id = random.randint(10000000, 99999999)
        all_profiles_for_card["sdvx_id"] = sdvx_id

    all_profiles_for_card["version"][str(game_version)] = {
        "game_version": game_version,
        "name": name,
        "appeal_id": 0,
        "skill_level": 0,
        "skill_base_id": 0,
        "skill_name_id": 0,
        "earned_gamecoin_packet": 0,
        "earned_gamecoin_block": 0,
        "earned_blaster_energy": 0,
        "earned_extrack_energy": 0,
        "used_packet_booster": 0,
        "used_block_booster": 0,
        "hispeed": 0,
        "lanespeed": 0,
        "gauge_option": 0,
        "ars_option": 0,
        "notes_option": 0,
        "early_late_disp": 0,
        "draw_adjust": 0,
        "eff_c_left": 0,
        "eff_c_right": 1,
        "music_id": 0,
        "music_type": 0,
        "sort_type": 0,
        "narrow_down": 0,
        "headphone": 1,
        "print_count": 0,
        "start_option": 0,
        "bgm": 0,
        "submonitor": 0,
        "nemsys": 0,
        "stampA": 0,
        "stampB": 0,
        "stampC": 0,
        "stampD": 0,
        "items": [],
        "params": [],
    }

    db.upsert(all_profiles_for_card, where("card") == dataid)

    response = E.response(
        E.game(
            E.result(0, __type="u8"),
        ),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_load")
async def game_sv6_load(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    dataid = request_info["root"][0].find("dataid").text
    profile = get_game_profile(dataid, game_version)

    if profile:
        djid, djid_split = get_id_from_profile(dataid)

        unlock = []
        for i in range(301):
            unlock.append([i, 11, 15])
        for i in range(6001):
            unlock.append([i, 1, 1])
        unlock.append([599, 4, 10])
        for item in profile["items"]:
            unlock.append(item)

        customize = [
            [
                2,
                2,
                [
                    profile["bgm"],
                    profile["submonitor"],
                    profile["nemsys"],
                    profile["stampA"],
                    profile["stampB"],
                    profile["stampC"],
                    profile["stampD"],
                ],
            ]
        ]
        for item in profile["params"]:
            customize.append(item)

        response = E.response(
            E.game(
                E.result(0, __type="u8"),
                E.name(profile["name"], __type="str"),
                E.code(djid_split, __type="str"),
                E.sdvx_id(djid_split, __type="str"),
                E.appeal_id(profile["appeal_id"], __type="u16"),
                E.skill_level(profile["skill_level"], __type="s16"),
                E.skill_base_id(profile["skill_base_id"], __type="s16"),
                E.skill_name_id(profile["skill_name_id"], __type="s16"),
                E.gamecoin_packet(profile["earned_gamecoin_packet"], __type="u32"),
                E.gamecoin_block(profile["earned_gamecoin_block"], __type="u32"),
                E.blaster_energy(profile["earned_blaster_energy"], __type="u32"),
                E.blaster_count(9999, __type="u32"),
                E.extrack_energy(profile["earned_extrack_energy"], __type="u16"),
                E.play_count(1001, __type="u32"),
                E.day_count(301, __type="u32"),
                E.today_count(21, __type="u32"),
                E.play_chain(31, __type="u32"),
                E.max_play_chain(31, __type="u32"),
                E.week_count(9, __type="u32"),
                E.week_play_count(101, __type="u32"),
                E.week_chain(31, __type="u32"),
                E.max_week_chain(1001, __type="u32"),
                E.creator_id(1, __type="u32"),
                E.eaappli(E.relation(1, __type="s8")),
                E.ea_shop(
                    E.blaster_pass_enable(1, __type="bool"),
                    E.blaster_pass_limit_date(1605871200, __type="u64"),
                ),
                E.kac_id(profile["name"], __type="str"),
                E.block_no(0, __type="s32"),
                E.volte_factory(
                    *[
                        E.info(
                            E.goods_id(s, __type="s32"),
                            E.status(1, __type="s32"),
                        )
                        for s in range(1, 999)
                    ],
                ),
                *[
                    E.campaign(
                        E.campaign_id(s, __type="s32"),
                        E.jackpot_flg(1, __type="bool"),
                    )
                    for s in range(99)
                ],
                E.cloud(E.relation(1, __type="s8")),
                E.something(
                    *[
                        E.info(
                            E.ranking_id(s[0], __type="s32"),
                            E.value(s[1], __type="s64"),
                        )
                        for s in [[1402, 20000]]
                    ],
                ),
                E.festival(
                    E.fes_id(1, __type="s32"),
                    E.live_energy(1000000, __type="s32"),
                    *[
                        E.bonus(
                            E.energy_type(s, __type="s32"),
                            E.live_energy(1000000, __type="s32"),
                        )
                        for s in range(1, 6)
                    ],
                ),
                E.valgene_ticket(
                    E.ticket_num(0, __type="s32"),
                    E.limit_date(1605871200, __type="u64"),
                ),
                E.arena(
                    E.last_play_season(0, __type="s32"),
                    E.rank_point(0, __type="s32"),
                    E.shop_point(0, __type="s32"),
                    E.ultimate_rate(0, __type="s32"),
                    E.ultimate_rank_num(0, __type="s32"),
                    E.rank_play_cnt(0, __type="s32"),
                    E.ultimate_play_cnt(0, __type="s32"),
                ),
                E.hispeed(profile["hispeed"], __type="s32"),
                E.lanespeed(profile["lanespeed"], __type="u32"),
                E.gauge_option(profile["gauge_option"], __type="u8"),
                E.ars_option(profile["ars_option"], __type="u8"),
                E.notes_option(profile["notes_option"], __type="u8"),
                E.early_late_disp(profile["early_late_disp"], __type="u8"),
                E.draw_adjust(profile["draw_adjust"], __type="s32"),
                E.eff_c_left(profile["eff_c_left"], __type="u8"),
                E.eff_c_right(profile["eff_c_right"], __type="u8"),
                E.last_music_id(profile["music_id"], __type="s32"),
                E.last_music_type(profile["music_type"], __type="u8"),
                E.sort_type(profile["sort_type"], __type="u8"),
                E.narrow_down(profile["narrow_down"], __type="u8"),
                E.headphone(profile["headphone"], __type="u8"),
                E.item(
                    *[
                        E.info(
                            E.id(s[0], __type="u32"),
                            E.type(s[1], __type="u8"),
                            E.param(s[2], __type="u32"),
                        )
                        for s in unlock
                    ],
                ),
                E.param(
                    *[
                        E.info(
                            E.type(s[0], __type="s32"),
                            E.id(s[1], __type="s32"),
                            E.param(s[2], __type="s32", __count=len(s[2])),
                        )
                        for s in customize
                    ],
                ),
            ),
        )

    else:
        response = E.response(
            E.game(
                E.result(1, __type="u8"),
            )
        )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_load_m")
async def game_sv6_load_m(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    dataid = request_info["root"][0].find("refid").text
    profile = get_game_profile(dataid, game_version)
    djid, djid_split = get_id_from_profile(dataid)

    best_scores = []
    db = get_db()
    for record in db.table("sdvx_scores_best").search(
        (where("game_version") == game_version) & (where("sdvx_id") == djid)
    ):
        best_scores.append(
            [
                record["music_id"],
                record["music_type"],
                record["score"],
                record["exscore"],
                record["clear_type"],
                record["score_grade"],
                0,
                0,
                record["btn_rate"],
                record["long_rate"],
                record["vol_rate"],
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]
        )

    response = E.response(
        E.game(
            E.music(
                *[
                    E.info(
                        E.param(x, __type="u32"),
                    )
                    for x in best_scores
                ],
            ),
        ),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_save")
async def game_sv6_save(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    dataid = request_info["root"][0].find("refid").text

    profile = get_profile(dataid)
    game_profile = profile["version"].get(str(game_version), {})

    root = request_info["root"][0]

    game_profile["appeal_id"] = int(root.find("appeal_id").text)

    nodes = [
        "appeal_id",
        "skill_level",
        "skill_base_id",
        "skill_name_id",
        "earned_gamecoin_packet",
        "earned_gamecoin_block",
        "earned_blaster_energy",
        "earned_extrack_energy",
        "hispeed",
        "lanespeed",
        "gauge_option",
        "ars_option",
        "notes_option",
        "early_late_disp",
        "draw_adjust",
        "eff_c_left",
        "eff_c_right",
        "music_id",
        "music_type",
        "sort_type",
        "narrow_down",
        "headphone",
        "start_option",
    ]

    for node in nodes:
        game_profile[node] = int(root.find(node).text)

    game_profile["used_packet_booster"] = int(root.find("ea_shop")[0].text)
    game_profile["used_block_booster"] = int(root.find("ea_shop")[1].text)
    game_profile["print_count"] = int(root.find("print")[0].text)

    items = []
    for info in root.find("item"):
        items.append(
            [
                int(info.find("id").text),
                int(info.find("type").text),
                int(info.find("param").text),
            ]
        )
    game_profile["items"] = items

    params = []
    for info in root.find("param"):
        p = info.find("param")
        params.append(
            [
                int(info.find("type").text),
                int(info.find("id").text),
                [int(x) for x in p.text.split(" ")],
            ]
        )
    game_profile["params"] = params

    profile["version"][str(game_version)] = game_profile

    get_db().table("sdvx_profile").upsert(profile, where("card") == dataid)

    response = E.response(
        E.game(),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_save_m")
async def game_sv6_save_m(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    timestamp = time.time()

    root = request_info["root"][0]

    dataid = root.find("dataid").text
    profile = get_game_profile(dataid, game_version)
    djid, djid_split = get_id_from_profile(dataid)

    track = root.find("track")
    play_id = int(track.find("play_id").text)
    music_id = int(track.find("music_id").text)
    music_type = int(track.find("music_type").text)
    score = int(track.find("score").text)
    exscore = int(track.find("exscore").text)
    clear_type = int(track.find("clear_type").text)
    score_grade = int(track.find("score_grade").text)
    max_chain = int(track.find("max_chain").text)
    just = int(track.find("just").text)
    critical = int(track.find("critical").text)
    near = int(track.find("near").text)
    error = int(track.find("error").text)
    effective_rate = int(track.find("effective_rate").text)
    btn_rate = int(track.find("btn_rate").text)
    long_rate = int(track.find("long_rate").text)
    vol_rate = int(track.find("vol_rate").text)
    mode = int(track.find("mode").text)
    gauge_type = int(track.find("gauge_type").text)
    notes_option = int(track.find("notes_option").text)
    online_num = int(track.find("online_num").text)
    local_num = int(track.find("local_num").text)
    challenge_type = int(track.find("challenge_type").text)
    retry_cnt = int(track.find("retry_cnt").text)
    judge = [int(x) for x in track.find("judge").text.split(" ")]

    db = get_db()
    db.table("sdvx_scores").insert(
        {
            "timestamp": timestamp,
            "game_version": game_version,
            "sdvx_id": djid,
            "play_id": play_id,
            "music_id": music_id,
            "music_type": music_type,
            "score": score,
            "exscore": exscore,
            "clear_type": clear_type,
            "score_grade": score_grade,
            "max_chain": max_chain,
            "just": just,
            "critical": critical,
            "near": near,
            "error": error,
            "effective_rate": effective_rate,
            "btn_rate": btn_rate,
            "long_rate": long_rate,
            "vol_rate": vol_rate,
            "mode": mode,
            "gauge_type": gauge_type,
            "notes_option": notes_option,
            "online_num": online_num,
            "local_num": local_num,
            "challenge_type": challenge_type,
            "retry_cnt": retry_cnt,
            "judge": judge,
        },
    )

    best = db.table("sdvx_scores_best").get(
        (where("sdvx_id") == djid)
        & (where("game_version") == game_version)
        & (where("music_id") == music_id)
        & (where("music_type") == music_type)
    )
    best = {} if best is None else best

    best_score_data = {
        "game_version": game_version,
        "sdvx_id": djid,
        "name": profile["name"],
        "music_id": music_id,
        "music_type": music_type,
        "score": max(score, best.get("score", score)),
        "exscore": max(exscore, best.get("exscore", exscore)),
        "clear_type": max(clear_type, best.get("clear_type", clear_type)),
        "score_grade": max(score_grade, best.get("score_grade", score_grade)),
        "btn_rate": max(btn_rate, best.get("btn_rate", btn_rate)),
        "long_rate": max(long_rate, best.get("long_rate", long_rate)),
        "vol_rate": max(vol_rate, best.get("vol_rate", vol_rate)),
    }

    db.table("sdvx_scores_best").upsert(
        best_score_data,
        (where("sdvx_id") == djid)
        & (where("game_version") == game_version)
        & (where("music_id") == music_id)
        & (where("music_type") == music_type),
    )

    response = E.response(
        E.game(),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_hiscore")
async def game_sv6_hiscore(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    best_scores = []
    db = get_db()
    for record in db.table("sdvx_scores_best").search(
        (where("game_version") == game_version)
    ):
        best_scores.append(
            [
                record["music_id"],
                record["music_type"],
                record["sdvx_id"],
                record["name"],
                record["score"],
            ]
        )

    response = E.response(
        E.game(
            E.sc(
                *[
                    E.d(
                        E.id(s[0], __type="u32"),
                        E.ty(s[1], __type="u32"),
                        E.a_sq(s[2], __type="str"),
                        E.a_nm(s[3], __type="str"),
                        E.a_sc(s[4], __type="u32"),
                        E.l_sq(s[2], __type="str"),
                        E.l_nm(s[3], __type="str"),
                        E.l_sc(s[4], __type="u32"),
                    )
                    for s in best_scores
                ],
            ),
        ),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_lounge")
async def game_sv6_lounge(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.game(E.interval(30, __type="u32")),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sv6_shop")
async def game_sv6_shop(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.game(E.nxt_time(1000 * 5 * 60, __type="u32")),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


for stub in [
    "load_r",
    "frozen",
    "save_e",
    "save_mega",
    "play_e",
    "play_s",
    "entry_s",
    "entry_e",
    "log",
]:

    @router.post(f"/{{gameinfo}}/game/sv6_{stub}")
    async def game_sv6_stub(request: Request):
        request_info = await core_process_request(request)

        response = E.response(
            E.game(),
        )

        response_body, response_headers = await core_prepare_response(request, response)
        return Response(content=response_body, headers=response_headers)
