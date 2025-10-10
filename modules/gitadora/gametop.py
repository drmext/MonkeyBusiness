from tinydb import Query, where

import time

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db


router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["M32"]


def get_profile(cid):
    return get_db().table("gitadora_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


@router.post("/{gameinfo}/{ver}_gametop/get")
async def gitadora_gametop_get(ver: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]
    spec = request_info["spec"]

    if spec in ("A", "C"):
        g = "guitarfreaks"
    elif spec in ("B", "D"):
        g = "drummania"

    data = request_info["root"][0].find("player")
    no = int(data.attrib["no"])
    dataid = data.find("refid").text
    profile = get_game_profile(dataid, game_version)
    gitadora_id = get_profile(dataid)["gitadora_id"]

    records = {}

    for record in (
        get_db().table(f"{g}_scores_best").search(where("gitadora_id") == gitadora_id)
    ):
        s = {
            "musicid": record["musicid"],
            "seq": record["seq"],
            "skill": record["skill"],
            "clear": record["clear"],
            "fullcombo": record["fullcombo"],
            "excellent": record["excellent"],
            "perc": record["perc"],
            "rank": record["rank"],
            "meter": record["meter"],
            "meter_prog": record["meter_prog"],
            "sdata": 0,
        }

        if record["musicid"] not in records:
            records[record["musicid"]] = {"order": len(records.keys()), "seq": {}}

        records[record["musicid"]]["seq"][record["seq"]] = s

    mlist = {}

    for musicid in records:
        data = {
            "musicid": musicid,
            "mdata": [-1] * 20,
            "flag": [0] * 5,
            "sdata": [-1] * 2,
            "meter": [0] * 8,
            "meter_prog": [-1] * 8,
        }

        for seq in records[musicid]["seq"]:
            seqidx = int(seq)
            data["mdata"][seqidx] = records[musicid]["seq"][seq]["perc"]
            data["mdata"][8 + seqidx] = (
                records[musicid]["seq"][seq]["rank"]
                if records[musicid]["seq"][seq]["clear"] != 0
                else -1
            )

            if records[musicid]["seq"][seq]["fullcombo"] != 0:
                data["flag"][0] |= 1 << seqidx

            if records[musicid]["seq"][seq]["excellent"] != 0:
                data["flag"][1] |= 1 << seqidx

            data["flag"][2] |= (
                records[musicid]["seq"][seq]["clear"] << seqidx
            )  # Clear flag/count score towards profile stats

            data["meter"][seqidx - 1] = records[musicid]["seq"][seq]["meter"]
            data["meter_prog"][seqidx - 1] = records[musicid]["seq"][seq]["meter_prog"]

        mlist[records[musicid]["order"]] = data

    mlist = [mlist[x] for x in sorted(mlist.keys(), key=lambda x: int(x))]

    if len(mlist) == 0:
        mlist = [
            {
                "musicid": -1,
                "mdata": [-1] * 20,
                "flag": [0] * 5,
                "sdata": [-1] * 2,
                "meter": [0] * 8,
                "meter_prog": [-1] * 8,
            }
        ]

    response = E.response(
        E(
            f"{ver}_gametop",
            E.player(
                E.now_date(round(time.time()), __type="u64"),
                E.musiclist(
                    *[
                        E.musicdata(
                            E.mdata(m["mdata"], __type="s16"),
                            E.flag(m["flag"], __type="u16"),
                            E.sdata(m["sdata"], __type="s16"),
                            E.meter(m["meter"], __type="u64"),
                            E.meter_prog(m["meter_prog"], __type="s16"),
                            musicid=m["musicid"],
                        )
                        for m in mlist
                    ],
                    nr=len(mlist),
                ),
                E.secretmusic(
                    E.music(
                        E.musicid(1, __type="s32"),
                        E.seq(1, __type="u16"),
                        E.kind(1, __type="s32"),
                    )
                ),
                E.chara_list(
                    E.chara(
                        E.charaid(1, __type="s32"),
                    )
                ),
                E.title_parts(
                    E.parts("", __type="str"),
                ),
                E.information(
                    E.info(profile[g]["information"], __type="u32"),
                ),
                E.reward(
                    E.status(profile[g]["reward"], __type="u32"),
                ),
                E.rivaldata(
                    *[
                        E.rival(
                            E.did(1, __type="s32"),
                            E.name("", __type="str"),
                            E.active_index(r_idx, __type="s32"),
                            E.refid(r, __type="str"),
                        )
                        for r_idx, r in enumerate(profile.get("rival_card_ids", []), 1)
                    ]
                ),
                E.frienddata(E.friend()),
                E.thanks_medal(
                    E.medal(profile[g]["thanks_medal_medal"], __type="s32"),
                    E.grant_medal(0, __type="s32"),
                    E.grant_total_medal(
                        profile[g]["thanks_medal_granted_total_medal"], __type="s32"
                    ),
                ),
                E.skindata(
                    E.skin([0xFFFFFFFF] * 100, __type="u32"),
                ),
                E.battledata(
                    E.info(
                        E.orb(0, __type="s32"),
                        E.get_gb_point(0, __type="s32"),
                        E.send_gb_point(0, __type="s32"),
                    ),
                    E.greeting(
                        E.greeting_1("hi", __type="str"),
                        E.greeting_2("hi", __type="str"),
                        E.greeting_3("hi", __type="str"),
                        E.greeting_4("hi", __type="str"),
                        E.greeting_5("hi", __type="str"),
                        E.greeting_6("hi", __type="str"),
                        E.greeting_7("hi", __type="str"),
                        E.greeting_8("hi", __type="str"),
                        E.greeting_9("hi", __type="str"),
                    ),
                    E.setting(
                        E.matching(1, __type="s32"),
                        E.info_level(1, __type="s32"),
                    ),
                    E.score(
                        E.battle_class(100, __type="s32"),
                        E.max_battle_class(100, __type="s32"),
                        E.battle_point(100, __type="s32"),
                        E.win(100, __type="s32"),
                        E.lose(100, __type="s32"),
                        E.draw(100, __type="s32"),
                        E.consecutive_win(100, __type="s32"),
                        E.max_consecutive_win(100, __type="s32"),
                        E.glorious_win(100, __type="s32"),
                        E.max_defeat_skill(100, __type="s32"),
                        E.latest_result(5, __type="s32"),
                    ),
                    E.history(),
                ),
                E.is_free_ok(0, __type="bool"),
                E.ranking(
                    E.skill(
                        E.rank(1, __type="s32"),
                        E.total_nr(1, __type="s32"),
                    ),
                    E.all_skill(
                        E.rank(1, __type="s32"),
                        E.total_nr(1, __type="s32"),
                    ),
                ),
                E.stage_result(),
                E.monthly_skill(),
                E.event_skill(
                    E.skill(1, __type="s32"),
                    E.ranking(
                        E.rank(1, __type="s32"),
                        E.total_nr(1, __type="s32"),
                    ),
                    E.eventlist(),
                ),
                E.event_score(E.event_list()),
                E.rockwave(E.score_list()),
                E.deluxe(
                    E.deluxe_content(0, __type="s32"),
                    E.target_id(0, __type="s32"),
                    E.multiply(0, __type="s32"),
                    E.point(0, __type="s32"),
                ),
                E.galaxy_parade(
                    E.score_list(),
                    E.last_corner_id(0, __type="s32"),
                    E.chara_list(),
                    E.last_sort_category(0, __type="s32"),
                    E.last_sort_order(0, __type="s32"),
                    E.team_member(
                        E.chara_id_guitar(0, __type="s32"),
                        E.chara_id_bass(0, __type="s32"),
                        E.chara_id_drum(0, __type="s32"),
                        E.chara_id_free1(0, __type="s32"),
                        E.chara_id_free2(0, __type="s32"),
                    ),
                ),
                E.livehouse(E.score_list(E.last_livehouse(0, __type="s32"))),
                E.jubeat_omiyage_challenge(),
                E.light_mode_reward_item(
                    E.itemid(-1, __type="s32"),
                    E.rarity(0, __type="s32"),
                ),
                E.standard_mode_reward_item(
                    E.itemid(-1, __type="s32"),
                    E.rarity(0, __type="s32"),
                ),
                E.delux_mode_reward_item(
                    E.itemid(-1, __type="s32"),
                    E.rarity(0, __type="s32"),
                ),
                E.kac2018(
                    E.entry_status(0, __type="s32"),
                    E.data(
                        E.term(0, __type="s32"),
                        E.total_score(0, __type="s32"),
                        E.score([0] * 6, __type="s32"),
                        E.music_type([0] * 6, __type="s32"),
                        E.play_count([0] * 6, __type="s32"),
                    ),
                ),
                E.sticker_campaign(),
                E.kac2017(
                    E.entry_status(0, __type="s32"),
                ),
                E.nostalgia_concert(),
                E.bemani_summer_2018(
                    E.linkage_id(-1, __type="s32"),
                    E.is_entry(0, __type="bool"),
                    E.target_music_idx(-1, __type="s32"),
                    E.point_1(0, __type="s32"),
                    E.point_2(0, __type="s32"),
                    E.point_3(0, __type="s32"),
                    E.point_4(0, __type="s32"),
                    E.point_5(0, __type="s32"),
                    E.point_6(0, __type="s32"),
                    E.point_7(0, __type="s32"),
                    E.reward_1(0, __type="bool"),
                    E.reward_2(0, __type="bool"),
                    E.reward_3(0, __type="bool"),
                    E.reward_4(0, __type="bool"),
                    E.reward_5(0, __type="bool"),
                    E.reward_6(0, __type="bool"),
                    E.reward_7(0, __type="bool"),
                    E.unlock_status_1(0, __type="s32"),
                    E.unlock_status_2(0, __type="s32"),
                    E.unlock_status_3(0, __type="s32"),
                    E.unlock_status_4(0, __type="s32"),
                    E.unlock_status_5(0, __type="s32"),
                    E.unlock_status_6(0, __type="s32"),
                    E.unlock_status_7(0, __type="s32"),
                ),
                E.thanksgiving(
                    E.term(0, __type="u8"),
                    E.score(
                        E.one_day_play_cnt(0, __type="s32"),
                        E.one_day_lottery_cnt(0, __type="s32"),
                        E.lucky_star(0, __type="s32"),
                        E.bear_mark(0, __type="s32"),
                        E.play_date_ms(0, __type="u64"),
                    ),
                    E.lottery_result(
                        E.unlock_bit(0, __type="u64"),
                    ),
                ),
                E.lotterybox(),
                E.long_otobear_fes_1(
                    E.point(0, __type="s32"),
                ),
                E.phrase_combo_challenge(
                    E.point(0, __type="s32"),
                ),
                *[
                    E(f"phrase_combo_challenge_{x}", E.point(0, __type="s32"))
                    for x in range(2, 21)
                ],
                E.bear_fes(
                    *[
                        E(
                            f"bear_fes_{x}",
                            E.stage(0, __type="s32"),
                            E.point([0] * 8, __type="s32"),
                        )
                        for x in range(1, 5)
                    ],
                ),
                E.monstar_subjugation(
                    *[
                        E(
                            f"monstar_subjugation_{x}",
                            E.stage(0, __type="s32"),
                            E.point_1(0, __type="s32"),
                            E.point_2(0, __type="s32"),
                            E.point_3(0, __type="s32"),
                        )
                        for x in range(1, 4)
                    ],
                ),
                *[
                    E(f"kouyou_challenge_{x}", E.point(0, __type="s32"))
                    for x in range(1, 4)
                ],
                E.sdvx_stamprally3(
                    E.point(0, __type="s32"),
                ),
                E.chronicle_1(
                    E.point(0, __type="s32"),
                ),
                E.playerboard(
                    E.index(1, __type="s32"),
                    E.is_active(1, __type="bool"),
                    E.sticker(
                        E.id(479, __type="s32"),
                        E.pos_x(160, __type="float"),
                        E.pos_y(235, __type="float"),
                        E.scale_x(1, __type="float"),
                        E.scale_y(1, __type="float"),
                        E.rotate(0, __type="float"),
                    ),
                    E.sticker(
                        E.id(172, __type="s32"),
                        E.pos_x(160, __type="float"),
                        E.pos_y(235, __type="float"),
                        E.scale_x(1, __type="float"),
                        E.scale_y(1, __type="float"),
                        E.rotate(0, __type="float"),
                    ),
                    E.sticker(
                        E.id(379, __type="s32"),
                        E.pos_x(175, __type="float"),
                        E.pos_y(175, __type="float"),
                        E.scale_x(0.4, __type="float"),
                        E.scale_y(0.4, __type="float"),
                        E.rotate(5, __type="float"),
                    ),
                    E.sticker(
                        E.id(172, __type="s32"),
                        E.pos_x(175, __type="float"),
                        E.pos_y(265, __type="float"),
                        E.scale_x(1, __type="float"),
                        E.scale_y(1, __type="float"),
                        E.rotate(0, __type="float"),
                    ),
                    E.sticker(
                        E.id(179, __type="s32"),
                        E.pos_x(69, __type="float"),
                        E.pos_y(420, __type="float"),
                        E.scale_x(1, __type="float"),
                        E.scale_y(1, __type="float"),
                        E.rotate(0, __type="float"),
                    ),
                ),
                E.player_info(
                    E.player_type(1, __type="s8"),
                    E.did(1, __type="s32"),
                    E.name(profile["name"], __type="str"),
                    E.title(profile["title"], __type="str"),
                    E.charaid(profile["charaid"], __type="s32"),
                ),
                E.customdata(
                    E.playstyle(profile[g]["customdata_playstyle"], __type="s32"),
                    E.custom(profile[g]["customdata_custom"], __type="s32"),
                ),
                E.playinfo(
                    E.cabid(profile[g]["playinfo_cabid"], __type="s32"),
                    E.play(profile[g]["playinfo_play"], __type="s32"),
                    E.playtime(profile[g]["playinfo_playtime"], __type="s32"),
                    E.playterm(profile[g]["playinfo_playterm"], __type="s32"),
                    E.session_cnt(profile[g]["playinfo_session_cnt"], __type="s32"),
                    E.matching_num(profile[g]["playinfo_matching_num"], __type="s32"),
                    E.extra_stage(profile[g]["playinfo_extra_stage"], __type="s32"),
                    E.extra_play(profile[g]["playinfo_extra_play"], __type="s32"),
                    E.extra_clear(profile[g]["playinfo_extra_clear"], __type="s32"),
                    E.encore_play(profile[g]["playinfo_encore_play"], __type="s32"),
                    E.encore_clear(profile[g]["playinfo_encore_clear"], __type="s32"),
                    E.pencore_play(profile[g]["playinfo_pencore_play"], __type="s32"),
                    E.pencore_clear(profile[g]["playinfo_pencore_clear"], __type="s32"),
                    E.max_clear_diff(
                        profile[g]["playinfo_max_clear_diff"], __type="s32"
                    ),
                    E.max_full_diff(profile[g]["playinfo_max_full_diff"], __type="s32"),
                    E.max_exce_diff(profile[g]["playinfo_max_exce_diff"], __type="s32"),
                    E.clear_num(profile[g]["playinfo_clear_num"], __type="s32"),
                    E.full_num(profile[g]["playinfo_full_num"], __type="s32"),
                    E.exce_num(profile[g]["playinfo_exce_num"], __type="s32"),
                    E.no_num(profile[g]["playinfo_no_num"], __type="s32"),
                    E.e_num(profile[g]["playinfo_e_num"], __type="s32"),
                    E.d_num(profile[g]["playinfo_d_num"], __type="s32"),
                    E.c_num(profile[g]["playinfo_c_num"], __type="s32"),
                    E.b_num(profile[g]["playinfo_b_num"], __type="s32"),
                    E.a_num(profile[g]["playinfo_a_num"], __type="s32"),
                    E.s_num(profile[g]["playinfo_s_num"], __type="s32"),
                    E.ss_num(profile[g]["playinfo_ss_num"], __type="s32"),
                    E.last_category(profile[g]["playinfo_last_category"], __type="s32"),
                    E.last_musicid(profile[g]["playinfo_last_musicid"], __type="s32"),
                    E.last_seq(profile[g]["playinfo_last_seq"], __type="s32"),
                    E.disp_level(profile[g]["playinfo_disp_level"], __type="s32"),
                ),
                E.tutorial(
                    E.progress(profile[g]["tutorial_progress"], __type="s32"),
                    E.disp_state(profile[g]["tutorial_disp_state"], __type="u32"),
                ),
                E.skilldata(
                    E.skill(profile[g]["skilldata_skill"], __type="s32"),
                    E.all_skill(profile[g]["skilldata_allskill"], __type="s32"),
                    E.old_skill(profile[g]["skilldata_skill"], __type="s32"),
                    E.old_all_skill(profile[g]["skilldata_allskill"], __type="s32"),
                ),
                E.favoritemusic(
                    E.list_1(profile[g]["favorite_music_list_1"], __type="s32"),
                    E.list_2(profile[g]["favorite_music_list_2"], __type="s32"),
                    E.list_3(profile[g]["favorite_music_list_3"], __type="s32"),
                ),
                E.recommend_musicid_list(
                    profile[g]["recommend_musicid_list"], __type="s32"
                ),
                E.record(
                    *[
                        E(
                            "gf" if g == "guitarfreaks" else "dm",
                            E.max_record(
                                E.skill(profile[g]["record_max_skill"], __type="s32"),
                                E.all_skill(
                                    profile[g]["record_max_all_skill"], __type="s32"
                                ),
                                E.clear_diff(
                                    profile[g]["record_max_clear_diff"], __type="s32"
                                ),
                                E.full_diff(
                                    profile[g]["record_max_full_diff"], __type="s32"
                                ),
                                E.exce_diff(
                                    profile[g]["record_max_exce_diff"], __type="s32"
                                ),
                                E.clear_music_num(
                                    profile[g]["record_max_clear_music_num"],
                                    __type="s32",
                                ),
                                E.full_music_num(
                                    profile[g]["record_max_full_music_num"],
                                    __type="s32",
                                ),
                                E.exce_music_num(
                                    profile[g]["record_max_exce_music_num"],
                                    __type="s32",
                                ),
                                E.clear_seq_num(
                                    profile[g]["record_max_clear_seq_num"], __type="s32"
                                ),
                                E.classic_all_skill(
                                    profile[g]["record_max_classic_all_skill"],
                                    __type="s32",
                                ),
                            ),
                            E.diff_record(
                                E.diff_100_nr(
                                    profile[g]["record_diff_100_nr"], __type="s32"
                                ),
                                E.diff_150_nr(
                                    profile[g]["record_diff_150_nr"], __type="s32"
                                ),
                                E.diff_200_nr(
                                    profile[g]["record_diff_200_nr"], __type="s32"
                                ),
                                E.diff_250_nr(
                                    profile[g]["record_diff_250_nr"], __type="s32"
                                ),
                                E.diff_300_nr(
                                    profile[g]["record_diff_300_nr"], __type="s32"
                                ),
                                E.diff_350_nr(
                                    profile[g]["record_diff_350_nr"], __type="s32"
                                ),
                                E.diff_400_nr(
                                    profile[g]["record_diff_400_nr"], __type="s32"
                                ),
                                E.diff_450_nr(
                                    profile[g]["record_diff_450_nr"], __type="s32"
                                ),
                                E.diff_500_nr(
                                    profile[g]["record_diff_500_nr"], __type="s32"
                                ),
                                E.diff_550_nr(
                                    profile[g]["record_diff_550_nr"], __type="s32"
                                ),
                                E.diff_600_nr(
                                    profile[g]["record_diff_600_nr"], __type="s32"
                                ),
                                E.diff_650_nr(
                                    profile[g]["record_diff_650_nr"], __type="s32"
                                ),
                                E.diff_700_nr(
                                    profile[g]["record_diff_700_nr"], __type="s32"
                                ),
                                E.diff_750_nr(
                                    profile[g]["record_diff_750_nr"], __type="s32"
                                ),
                                E.diff_800_nr(
                                    profile[g]["record_diff_800_nr"], __type="s32"
                                ),
                                E.diff_850_nr(
                                    profile[g]["record_diff_850_nr"], __type="s32"
                                ),
                                E.diff_900_nr(
                                    profile[g]["record_diff_900_nr"], __type="s32"
                                ),
                                E.diff_950_nr(
                                    profile[g]["record_diff_950_nr"], __type="s32"
                                ),
                                E.diff_100_clear(
                                    profile[g]["record_diff_100_clear"], __type="s32"
                                ),
                                E.diff_150_clear(
                                    profile[g]["record_diff_150_clear"], __type="s32"
                                ),
                                E.diff_200_clear(
                                    profile[g]["record_diff_200_clear"], __type="s32"
                                ),
                                E.diff_250_clear(
                                    profile[g]["record_diff_250_clear"], __type="s32"
                                ),
                                E.diff_300_clear(
                                    profile[g]["record_diff_300_clear"], __type="s32"
                                ),
                                E.diff_350_clear(
                                    profile[g]["record_diff_350_clear"], __type="s32"
                                ),
                                E.diff_400_clear(
                                    profile[g]["record_diff_400_clear"], __type="s32"
                                ),
                                E.diff_450_clear(
                                    profile[g]["record_diff_450_clear"], __type="s32"
                                ),
                                E.diff_500_clear(
                                    profile[g]["record_diff_500_clear"], __type="s32"
                                ),
                                E.diff_550_clear(
                                    profile[g]["record_diff_550_clear"], __type="s32"
                                ),
                                E.diff_600_clear(
                                    profile[g]["record_diff_600_clear"], __type="s32"
                                ),
                                E.diff_650_clear(
                                    profile[g]["record_diff_650_clear"], __type="s32"
                                ),
                                E.diff_700_clear(
                                    profile[g]["record_diff_700_clear"], __type="s32"
                                ),
                                E.diff_750_clear(
                                    profile[g]["record_diff_750_clear"], __type="s32"
                                ),
                                E.diff_800_clear(
                                    profile[g]["record_diff_800_clear"], __type="s32"
                                ),
                                E.diff_850_clear(
                                    profile[g]["record_diff_850_clear"], __type="s32"
                                ),
                                E.diff_900_clear(
                                    profile[g]["record_diff_900_clear"], __type="s32"
                                ),
                                E.diff_950_clear(
                                    profile[g]["record_diff_950_clear"], __type="s32"
                                ),
                            ),
                        )
                        for g in ["guitarfreaks", "drummania"]
                    ],
                ),
                E.groove(
                    E.extra_gauge(profile[g]["groove_extra_gauge"], __type="s32"),
                    E.encore_gauge(profile[g]["groove_encore_gauge"], __type="s32"),
                    E.encore_cnt(profile[g]["groove_encore_cnt"], __type="s32"),
                    E.encore_success(profile[g]["groove_encore_success"], __type="s32"),
                    E.unlock_point(profile[g]["groove_unlock_point"], __type="s32"),
                ),
                E.finish(1, __type="bool"),
                no=no,
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
