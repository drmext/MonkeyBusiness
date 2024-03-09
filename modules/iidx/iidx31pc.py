from tinydb import Query, where

from time import time
import config
import random

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["LDJ"]


def get_profile(cid):
    return get_db().table("iidx_profile").get(where("card") == cid)


def get_profile_by_id(iidx_id):
    return get_db().table("iidx_profile").get(where("iidx_id") == iidx_id)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


def get_game_profile_by_id(iidx_id, game_version):
    profile = get_profile_by_id(iidx_id)

    return profile["version"].get(str(game_version), None)


def get_id_from_profile(cid):
    profile = get_db().table("iidx_profile").get(where("card") == cid)

    djid = "%08d" % profile["iidx_id"]
    djid_split = "-".join([djid[:4], djid[4:]])

    return profile["iidx_id"], djid_split


def calculate_folder_mask(profile):
    return (
        profile.get("_show_category_grade", 0) << 0
        | (profile.get("_show_category_status", 0) << 1)
        | (profile.get("_show_category_difficulty", 0) << 2)
        | (profile.get("_show_category_alphabet", 0) << 3)
        | (profile.get("_show_category_rival_play", 0) << 4)
        | (profile.get("_show_category_rival_winlose", 0) << 6)
        | (profile.get("_show_rival_shop_info", 0) << 7)
        | (profile.get("_hide_play_count", 0) << 8)
        | (profile.get("_show_score_graph_cutin", 0) << 9)
        | (profile.get("_classic_hispeed", 0) << 10)
        | (profile.get("_hide_iidx_id", 0) << 12)
    )


@router.post("/{gameinfo}/IIDX31pc/get")
async def iidx31pc_get(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]
    date_code = int(request_info["ext"])

    cid = request_info["root"][0].attrib["cid"]
    profile = get_game_profile(cid, game_version)
    djid, djid_split = get_id_from_profile(cid)

    rival_ids = [
        profile.get("sp_rival_1_iidx_id", 0),
        profile.get("sp_rival_2_iidx_id", 0),
        profile.get("sp_rival_3_iidx_id", 0),
        profile.get("sp_rival_4_iidx_id", 0),
        profile.get("sp_rival_5_iidx_id", 0),
        profile.get("sp_rival_6_iidx_id", 0),
        profile.get("dp_rival_1_iidx_id", 0),
        profile.get("dp_rival_2_iidx_id", 0),
        profile.get("dp_rival_3_iidx_id", 0),
        profile.get("dp_rival_4_iidx_id", 0),
        profile.get("dp_rival_5_iidx_id", 0),
        profile.get("dp_rival_6_iidx_id", 0),
    ]
    rivals = {}
    for idx, r in enumerate(rival_ids):
        if r == 0:
            continue
        rivals[idx] = {}
        rivals[idx]["spdp"] = 1 if idx < 6 else 2

        rival_profile = get_game_profile_by_id(r, game_version)
        rdjid = "%08d" % r
        rdjid_split = "-".join([rdjid[:4], rdjid[4:]])

        rivals[idx]["djid"] = rdjid
        rivals[idx]["djid_split"] = rdjid_split
        rivals[idx]["djname"] = rival_profile["djname"]
        rivals[idx]["region"] = rival_profile["region"]
        rivals[idx]["sa"] = rival_profile["sach"]
        rivals[idx]["sg"] = rival_profile["grade_single"]
        rivals[idx]["da"] = rival_profile["dach"]
        rivals[idx]["dg"] = rival_profile["grade_double"]
        rivals[idx]["body"] = rival_profile["body"]
        rivals[idx]["face"] = rival_profile["face"]
        rivals[idx]["hair"] = rival_profile["hair"]
        rivals[idx]["hand"] = rival_profile["hand"]
        rivals[idx]["head"] = rival_profile["head"]

    # current_time = round(time())

    response = E.response(
        E.IIDX31pc(
            E.pcdata(
                d_auto_adjust=profile["d_auto_adjust"],
                d_auto_scrach=profile["d_auto_scrach"],
                d_camera_layout=profile["d_camera_layout"],
                d_classic_hispeed=profile["d_classic_hispeed"],
                d_disp_judge=profile["d_disp_judge"],
                d_exscore=profile["d_exscore"],
                d_gauge_disp=profile["d_gauge_disp"],
                d_ghost_score=profile["d_ghost_score"],
                d_gno=profile["d_gno"],
                d_graph_score=profile["d_graph_score"],
                d_gtype=profile["d_gtype"],
                d_hispeed=profile["d_hispeed"],
                d_judge=profile["d_judge"],
                d_judgeAdj=profile["d_judgeAdj"],
                d_lane_brignt=profile["d_lane_brignt"],
                d_liflen=profile["d_liflen"],
                d_notes=profile["d_notes"],
                d_opstyle=profile["d_opstyle"],
                d_pace=profile["d_pace"],
                d_sdlen=profile["d_sdlen"],
                d_sdtype=profile["d_sdtype"],
                d_sorttype=profile["d_sorttype"],
                d_sub_gno=profile["d_sub_gno"],
                d_timing=profile["d_timing"],
                d_timing_split=profile["d_timing_split"],
                d_tsujigiri_disp=profile["d_tsujigiri_disp"],
                d_tune=profile["d_tune"],
                d_visualization=profile["d_visualization"],
                dach=profile["dach"],
                dp_opt=profile["dp_opt"],
                dp_opt2=profile["dp_opt2"],
                dpnum=profile["dpnum"],
                gpos=profile["gpos"],
                id=djid,
                idstr=djid_split,
                mode=profile["mode"],
                name=profile["djname"],
                ngrade=profile["ngrade"],
                pid=profile["region"],
                player_kind=-1,
                pmode=profile["pmode"],
                rtype=profile["rtype"],
                s_auto_adjust=profile["s_auto_adjust"],
                s_auto_scrach=profile["s_auto_scrach"],
                s_camera_layout=profile["s_camera_layout"],
                s_classic_hispeed=profile["s_classic_hispeed"],
                s_disp_judge=profile["s_disp_judge"],
                s_exscore=profile["s_exscore"],
                s_gauge_disp=profile["s_gauge_disp"],
                s_ghost_score=profile["s_ghost_score"],
                s_gno=profile["s_gno"],
                s_graph_score=profile["s_graph_score"],
                s_gtype=profile["s_gtype"],
                s_hispeed=profile["s_hispeed"],
                s_judge=profile["s_judge"],
                s_judgeAdj=profile["s_judgeAdj"],
                s_lane_brignt=profile["s_lane_brignt"],
                s_liflen=profile["s_liflen"],
                s_notes=profile["s_notes"],
                s_opstyle=profile["s_opstyle"],
                s_pace=profile["s_pace"],
                s_sdlen=profile["s_sdlen"],
                s_sdtype=profile["s_sdtype"],
                s_sorttype=profile["s_sorttype"],
                s_sub_gno=profile["s_sub_gno"],
                s_timing=profile["s_timing"],
                s_timing_split=profile["s_timing_split"],
                s_tsujigiri_disp=profile["s_tsujigiri_disp"],
                s_tune=profile["s_tune"],
                s_visualization=profile["s_visualization"],
                sach=profile["sach"],
                sp_opt=profile["sp_opt"],
                spnum=profile["spnum"],
            ),
            E.qprodata(
                [
                    profile["head"],
                    profile["hair"],
                    profile["face"],
                    profile["hand"],
                    profile["body"],
                ],
                __type="u32",
                __size=5 * 4,
            ),
            E.skin(
                [
                    calculate_folder_mask(profile),
                    profile["explosion"],
                    profile["explosion_size"],
                    profile["turntable"],
                    profile["judgestring"],
                    profile["note"],
                    profile.get("note_size", 0),
                    profile["soundpreview"],
                    profile["effector_lock"],
                    profile["effector_type"],
                    profile["bgm"],
                    profile["alternate_hcn"],
                    profile["kokokara_start"],
                    profile["sudden"],
                    profile["grapharea"],
                    profile.get("lift", 0),
                    profile["keybeam"],
                    profile.get("keybeam_size", 1),
                    profile["fullcombo"],
                    0,
                ],
                __type="s32" if date_code >= 2024011600 else "s16",
            ),
            E.tdjskin(
                [
                    profile.get("submonitor", 0),
                    0,
                    0,
                    0,
                ],
                __type="s16",
            ),
            E.skin_customize_flg(
                skin_frame_flg=-1,
                skin_turntable_flg=-1,
                skin_bomb_flg=-1,
                skin_bgm_flg=-1,
                skin_lane_flg0=-1,
                skin_lane_flg1=-1,
                skin_lane_flg2=-1,
                skin_lane_flg3=-1,
                skin_lane_flg4=-1,
                skin_lane_flg5=-1,
                skin_notes_flg=-1,
                skin_fullcombo_flg=-1,
                skin_keybeam_flg=-1,
                skin_judgestring_flg=-1,
                # skin_bgm_flg=profile["skin_customize_flag_bgm"],
                # skin_lane_flg3=profile["skin_customize_flag_lane"],
            ),
            E.tdjskin_customize_flg(
                skin_submonitor_flg=-1,
            ),
            E.spdp_rival(
                flg=-1
            ),  # required for rivals to load after switching spdp in music select
            E.rlist(
                *[
                    E.rival(
                        E.is_robo(0, __type="bool"),
                        E.shop(name=config.arcade),
                        E.qprodata(
                            body=rivals[r]["body"],
                            face=rivals[r]["face"],
                            hair=rivals[r]["hair"],
                            hand=rivals[r]["hand"],
                            head=rivals[r]["head"],
                        ),
                        da=rivals[r]["da"],
                        dg=rivals[r]["dg"],
                        djname=rivals[r]["djname"],
                        id=rivals[r]["djid"],
                        id_str=rivals[r]["djid_split"],
                        pid=rivals[r]["region"],
                        sa=rivals[r]["sa"],
                        sg=rivals[r]["sg"],
                        spdp=rivals[r]["spdp"],
                    )
                    for r in rivals
                ],
            ),
            E.deller(deller=profile["deller"], rate=0),
            E.secret(
                E.flg1(profile.get("secret_flg1", [-1, -1, -1]), __type="s64"),
                E.flg2(profile.get("secret_flg2", [-1, -1, -1]), __type="s64"),
                E.flg3(profile.get("secret_flg3", [-1, -1, -1]), __type="s64"),
                E.flg4(profile.get("secret_flg4", [-1, -1, -1]), __type="s64"),
            ),
            E.join_shop(join_cflg=1, join_id=10, join_name=config.arcade, joinflg=1),
            E.leggendaria(
                E.flg1(profile.get("leggendaria_flg1", [-1, -1, -1]), __type="s64")
            ),
            E.grade(
                *[E.g(x, __type="u8") for x in profile["grade_values"]],
                dgid=profile["grade_double"],
                sgid=profile["grade_single"],
            ),
            E.world_tourism_secret_flg(
                E.flg1(profile.get("wt_flg1", [-1, -1, -1]), __type="s64"),
                E.flg2(profile.get("wt_flg2", [-1, -1, -1]), __type="s64"),
            ),
            E.world_tourism_setting(
                E.booster(1, __type="bool"),
            ),
            E.world_tourism(
                *[
                    E.tour_data(
                        tour_id=i,
                        progress=50,  # set to 49 to see WT folders, 50 is completed/hidden
                    )
                    for i in range(16)
                ],
            ),
            E.lightning_setting(
                E.slider(
                    profile.get("lightning_setting_slider", [0] * 7), __type="s32"
                ),
                E.light(
                    profile.get("lightning_setting_light", [1] * 10), __type="bool"
                ),
                E.concentration(
                    profile.get("lightning_setting_concentration", 0), __type="bool"
                ),
                headphone_vol=profile.get("lightning_setting_headphone_vol", 0),
                resistance_sp_left=profile.get(
                    "lightning_setting_resistance_sp_left", 0
                ),
                resistance_sp_right=profile.get(
                    "lightning_setting_resistance_sp_right", 0
                ),
                resistance_dp_left=profile.get(
                    "lightning_setting_resistance_dp_left", 0
                ),
                resistance_dp_right=profile.get(
                    "lightning_setting_resistance_dp_right", 0
                ),
                keyboard_kind=profile.get("lightning_setting_keyboard_kind", 0),
            ),
            E.arena_data(
                E.achieve_data(
                    play_style=0,
                    arena_class=19,
                    rating_value=90,
                    now_top_class_continuing=19,
                    best_top_class_continuing=19,
                    win_count=0,
                    now_winning_streak_count=0,
                    best_winning_streak_count=0,
                    perfect_win_count=0,
                    counterattack_num=0,
                    mission_clear_num=0,
                ),
                E.achieve_data(
                    play_style=1,
                    arena_class=19,
                    rating_value=90,
                    now_top_class_continuing=19,
                    best_top_class_continuing=19,
                    win_count=0,
                    now_winning_streak_count=0,
                    best_winning_streak_count=0,
                    perfect_win_count=0,
                    counterattack_num=0,
                    mission_clear_num=0,
                ),
                E.cube_data(
                    cube=200,
                    season_id=0,
                ),
                E.ranker_data(
                    play_style=0,
                    pref_id=0,
                    rank_num=(random.choice([random.randint(1, 5), 573])),
                ),
                E.ranker_data(
                    play_style=1,
                    pref_id=0,
                    rank_num=(random.choice([random.randint(1, 5), 573])),
                ),
                E.lose_data(
                    play_style=0,
                    lose_value=0,
                ),
                E.lose_data(
                    play_style=1,
                    lose_value=0,
                ),
                E.chat_data(
                    E.is_chat_0(1, __type="bool"),
                    E.is_chat_1(1, __type="bool"),
                    E.is_chat_2(1, __type="bool"),
                    E.is_chat_3(1, __type="bool"),
                    chat_type_0="hi",
                    chat_type_1="やあ",
                    chat_type_2="こんにちは",
                    chat_type_3="おす",
                ),
                E.tendency(
                    play_style=0,
                    rank0=1,
                    rank1=2,
                    rank2=3,
                    rank3=4,
                    rank4=3,
                    rank5=1,
                ),
                #E.player_kind_data(
                #    kind=(random.choice([random.randint(0, 13), 0])),
                #),
                E.setting(
                    E.hide_shopname(0, __type="bool"),
                    stats_type=0,
                ),
                E.qpro_motion(
                    motion_0=1,
                    motion_1=2,
                    motion_2=3,
                ),
                play_num=6,
                play_num_dp=3,
                play_num_sp=3,
                prev_best_class_sp=18,
                prev_best_class_dp=18,
            ),
            E.bind_eaappli(),
            E.ea_premium_course(),
            E.language_setting(language=profile["language_setting"]),
            E.movie_agreement(agreement_version=profile["movie_agreement"]),
            E.movie_setting(
                E.hide_name(0, __type="bool"),
            ),
            E.lightning_play_data(
                spnum=profile["lightning_play_data_spnum"],
                dpnum=profile["lightning_play_data_dpnum"],
            ),
            E.weekly(
                mid=-1,
                wid=1,
            ),
            E.packinfo(
                music_0=-1,
                music_1=-1,
                music_2=-1,
                pack_id=1,
            ),
            E.kac_entry_info(
                E.enable_kac_deller(),
                E.disp_kac_mark(),
                E.is_kac_entry(),
                E.is_kac_evnet_entry(),
                E.kac_secret_music(
                    E.music_info(
                        index=0,
                        music_id=1000,
                    ),
                ),
            ),
            E.orb_data(
                rest_orb=100,
                present_orb=100,
            ),
            E.visitor(anum=1, pnum=2, snum=1, vs_flg=1),
            E.old_linkage_secret_flg(
                bemani_mixup=-1,
                ccj_linkage=-1,
                triple_tribe=-1,
            ),
            E.ultimate_mobile_link(E.link_flag(), music_list=-1),
            E.valkyrie_linkage(music_list_1=-1, music_list_2=-1, music_list_3=-1),
            E.ccj_linkage(music_list=-1),
            E.triple_tribe_2(music_list=-1),
            E.achievements(
                # E.trophy(profile.get("achievements_trophy", [])[:10], __type="s64"),
                pack=profile.get("achievements_pack_id", 0),
                pack_comp=profile.get("achievements_pack_comp", 0),
                last_weekly=profile.get("achievements_last_weekly", 0),
                weekly_num=profile.get("achievements_weekly_num", 0),
                visit_flg=profile.get("achievements_visit_flg", 0),
                rival_crush=0,
            ),
            E.notes_radar(
                E.radar_score(
                    profile["notes_radar_single"],
                    __type="s32",
                ),
                style=0,
            ),
            E.notes_radar(
                E.radar_score(
                    profile["notes_radar_double"],
                    __type="s32",
                ),
                style=1,
            ),
            E.dj_rank(
                E.rank(
                    profile["dj_rank_single_rank"],
                    __type="s32",
                ),
                E.point(
                    profile["dj_rank_single_point"],
                    __type="s32",
                ),
                style=0,
            ),
            E.dj_rank(
                E.rank(
                    profile["dj_rank_double_rank"],
                    __type="s32",
                ),
                E.point(
                    profile["dj_rank_double_point"],
                    __type="s32",
                ),
                style=1,
            ),
            E.step(
                E.is_track_ticket(
                    profile["stepup_is_track_ticket"],
                    __type="bool",
                ),
                dp_fluctuation=profile["stepup_dp_fluctuation"],
                dp_level=profile["stepup_dp_level"],
                dp_mplay=profile["stepup_dp_mplay"],
                enemy_damage=profile["stepup_enemy_damage"],
                enemy_defeat_flg=profile["stepup_enemy_defeat_flg"],
                mission_clear_num=profile["stepup_mission_clear_num"],
                progress=profile["stepup_progress"],
                sp_fluctuation=profile["stepup_sp_fluctuation"],
                sp_level=profile["stepup_sp_level"],
                sp_mplay=profile["stepup_sp_mplay"],
                tips_read_list=profile["stepup_tips_read_list"],
                total_point=profile["stepup_total_point"],
            ),
            E.tsujigiri(total_num_sp=287, total_num_dp=286),
            E.tsujigiri_hidden_chara(
                E.appearance_info(
                    appearance_id=1,
                    music_0=-1,
                    music_1=-1,
                    music_2=-1,
                    chara_0=-1,
                    chara_1=-1,
                    chara_2=-1,
                ),
                E.defeat(defeat_flg=0),
                E.total_defeat(
                    E.chara(
                        id=0,
                        num=0,
                    )
                ),
            ),
            E.music_memo(
                *[
                    E.folder(
                        E.music_id(
                            profile.get(f"music_memo_{fi}_{ps}_mids", [0] * 10),
                            __type="s32",
                        ),
                        play_style=ps,
                        folder_id=fi,
                        name=profile.get(
                            f"music_memo_{fi}_{ps}_name", f"FOLDER {str(fi+1).zfill(2)}"
                        ),
                    )
                    for fi in range(10)
                    for ps in range(2)
                ],
            ),
            # ),
            # E.event_1(
            #     E.flyer_data(
            #         flyer_id=0,
            #         play_num=0,
            #         last_select_genre=0,
            #         flyer_prog=0,
            #         skill_param=0,
            #     ),
            #     E.genre_data(
            #         E.is_complete(0, __type="bool"),
            #         flyer_id=0,
            #         genre_id=0,
            #         play_num=0,
            #         gauge=0,
            #     ),
            #     event_play_num=0,
            #     last_select_flyer_id=0,
            # ),
            # E.player_compe(
            #     E.compe_data(
            #         E.compe_music(
            #             index=0,
            #             music_id=26029,
            #             style_id=0,
            #             note_grade_id=3,
            #             ex_score=6,
            #             pgreat_num=6,
            #             great_num=6,
            #             miss_num=6,
            #         ),
            #         E.compe_music(
            #             index=1,
            #             music_id=29057,
            #             style_id=0,
            #             note_grade_id=3,
            #             ex_score=6,
            #             pgreat_num=6,
            #             great_num=6,
            #             miss_num=6,
            #         ),
            #         E.compe_music(
            #             index=2,
            #             music_id=8027,
            #             style_id=0,
            #             note_grade_id=3,
            #             ex_score=6,
            #             pgreat_num=6,
            #             great_num=6,
            #             miss_num=6,
            #         ),
            #         E.compe_music(
            #             index=3,
            #             music_id=16027,
            #             style_id=0,
            #             note_grade_id=3,
            #             ex_score=6,
            #             pgreat_num=6,
            #             great_num=6,
            #             miss_num=6,
            #         ),
            #         compe_id=0,
            #         forced_option=1,
            #         compe_end_time=current_time,
            #         compe_name="Monkey Business",
            #         maker_name="kors k",
            #         ex_score=666,
            #         pgreat_num=666,
            #         great_num=666,
            #         my_rank=1,
            #         total_join=1,
            #     ),
            # ),
            # E.news(
            #     *[E(x,
            #         E.detail(
            #             music_id=1000,
            #             class_id=3,
            #             news_type=0,
            #             news_data=1572,
            #             news_time=current_time,
            #             dj_name="TEST",
            #         ),
            #         last_read_time=current_time,
            #     )for x in ("news_data_all", "news_data_shop", "news_data_grade", "news_data_rival", "news_data_all_top", "news_data_area_top", "news_data_shop_top")],
            # disp_score_type=0,
            # ),
            # E.exam_data(
            #     E.music(
            #         radar_type=1,
            #         index=0,
            #         music_id=26029,
            #         class_id=3,
            #         rank=1,
            #         score=1,
            #     ),
            #     E.music(
            #         radar_type=1,
            #         index=1,
            #         music_id=29057,
            #         class_id=3,
            #         rank=1,
            #         score=1,
            #     ),
            #     E.music(
            #         radar_type=1,
            #         index=2,
            #         music_id=8027,
            #         class_id=3,
            #         rank=1,
            #         score=1,
            #     ),
            #     E.music(
            #         radar_type=1,
            #         index=3,
            #         music_id=16027,
            #         class_id=3,
            #         rank=1,
            #         score=1,
            #     ),
            #     exam_id=0,
            #     entry_num=1,
            #     rank=1,
            #     total_score=1,
            #     end_time=current_time,
            # ),
            # E.questionnaire(
            #     *[E.questionnaire_data(
            #         questionnaire_id=i,
            #         answer="what is this?"
            #     )for i in range(10)],
            # ),
            # E.badge(
            #     # Base
            #     E.badge_data(
            #         category_id=1,
            #         badge_flg_id=23,
            #         badge_flg=554321,
            #     ),
            #     E.badge_data(
            #         category_id=1,
            #         badge_flg_id=11,
            #         badge_flg=554321,
            #     ),
            #     E.badge_equip(
            #         E.equip_flg(1, __type="bool"),
            #         category_id=1,
            #         badge_flg_id=23,
            #         index=5,
            #         slot=0,
            #     ),
            #     E.badge_equip(
            #         E.equip_flg(1, __type="bool"),
            #         category_id=1,
            #         badge_flg_id=11,
            #         index=5,
            #         slot=4,
            #     ),
            #     # Class
            #     E.badge_data(
            #         category_id=2,
            #         badge_flg_id=0,
            #         badge_flg=191919191919,
            #     ),
            #     E.badge_equip(
            #         E.equip_flg(1, __type="bool"),
            #         category_id=2,
            #         badge_flg_id=0,
            #         index=2,
            #         slot=3,
            #     ),
            #     E.badge_equip(
            #         E.equip_flg(1, __type="bool"),
            #         category_id=2,
            #         badge_flg_id=0,
            #         index=5,
            #         slot=1,
            #     ),
            #     # Radar Rank
            #     E.badge_data(
            #         category_id=7,
            #         badge_flg_id=1,
            #         badge_flg=1010101010,
            #     ),
            #     E.badge_equip(
            #         E.equip_flg(1, __type="bool"),
            #         category_id=7,
            #         badge_flg_id=1,
            #         index=2,
            #         slot=2,
            #     ),
            # ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/common")
async def iidx31pc_common(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX31pc(
            # E.monthly_mranking(
            #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #     __type="u16",
            # ),
            # E.total_mranking(
            #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            #     __type="u16",
            # ),
            # E.boss(phase=0),  # disable event
            # E.world_tourism(open_list=1),
            # E.bpl_virtual(),
            # E.bpl_battle(phase=1),
            E.kac_mid([-1, -1, -1, -1, -1], __type="s32"),
            E.kac_clid([2, 2, 2, 2, 2], __type="s32"),
            E.ir(beat=3),
            E.cm(compo="cm_bpl", folder="cm", id=0),
            # E.tdj_cm(
            #     E.cm(filename="cm_bpls3sdvx", id=0),
            #     E.cm(filename="cm_paseli2023nov", id=1),
            # ),
            # E.playvideo_disable_music(E.music(musicid=-1)),
            # E.music_movie_suspend(E.music(music_id=-1, kind=0, name='')),
            E.movie_agreement(version=1),
            E.license("None", __type="str"),
            E.file_recovery(url=str(config.ip)),
            E.movie_upload(url=str(config.ip)),
            # E.button_release_frame(frame=''),
            # E.trigger_logic_type(type=''),
            # E.cm_movie_info(type=''),
            E.escape_package_info(),
            E.vip_pass_black(),
            E.deller_bonus(open=1),
            # E.pcb_check(flg=0)
            E.common_evnet(flg=-1),
            E.system_voice_phase(phase=random.randint(1, 10)),  # TODO: Figure out range
            # E.disable_same_triger(frame=-1),
            E.play_video(),
            E.music_retry(),
            E.display_asio_logo(),
            # E.force_rom_check(),
            # E.hitchart(),
            E.lane_gacha(),
            # E.fps_fix(),
            # E.save_unsync_log(),
            # E.fix_framerate(),
            # E.fix_real(),
            # E.tourism_booster(),
            # E.questionnaire_list(),
            expire=600,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/save")
async def iidx31pc_save(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    xid = int(request_info["root"][0].attrib["iidxid"])
    cid = request_info["root"][0].attrib["cid"]
    clt = int(request_info["root"][0].attrib["cltype"])

    profile = get_profile(cid)
    game_profile = profile["version"].get(str(game_version), {})

    for k in [
        "d_auto_adjust",
        "d_auto_scrach",
        "d_camera_layout",
        "d_classic_hispeed",
        "d_disp_judge",
        "d_gauge_disp",
        "d_ghost_score",
        "d_gno",
        "d_graph_score",
        "d_gtype",
        "d_hispeed",
        "d_judge",
        "d_judgeAdj",
        "d_lane_brignt",
        "d_notes",
        "d_opstyle",
        "d_pace",
        "d_sdlen",
        "d_sdtype",
        "d_sorttype",
        "d_sub_gno",
        "d_timing",
        "d_timing_split",
        "d_tsujigiri_disp",
        "d_visualization",
        "dp_opt",
        "dp_opt2",
        "gpos",
        "mode",
        "ngrade",
        "pmode",
        "rtype",
        "s_auto_adjust",
        "s_auto_scrach",
        "s_camera_layout",
        "s_classic_hispeed",
        "s_disp_judge",
        "s_gauge_disp",
        "s_ghost_score",
        "s_gno",
        "s_graph_score",
        "s_gtype",
        "s_hispeed",
        "s_judge",
        "s_judgeAdj",
        "s_lane_brignt",
        "s_notes",
        "s_opstyle",
        "s_pace",
        "s_sdlen",
        "s_sdtype",
        "s_sorttype",
        "s_sub_gno",
        "s_timing",
        "s_timing_split",
        "s_tsujigiri_disp",
        "s_visualization",
        "sp_opt",
    ]:
        if k in request_info["root"][0].attrib:
            game_profile[k] = request_info["root"][0].attrib[k]

    for k in [
        ("d_liflen", "d_lift"),
        ("dach", "d_achi"),
        ("s_liflen", "s_lift"),
        ("sach", "s_achi"),
    ]:
        if k[1] in request_info["root"][0].attrib:
            game_profile[k[0]] = request_info["root"][0].attrib[k[1]]

    lightning_setting = request_info["root"][0].find("lightning_setting")
    if lightning_setting is not None:
        for k in [
            "headphone_vol",
            "resistance_dp_left",
            "resistance_dp_right",
            "resistance_sp_left",
            "resistance_sp_right",
            "keyboard_kind",
        ]:
            game_profile["lightning_setting_" + k] = int(lightning_setting.attrib[k])

        slider = lightning_setting.find("slider")
        if slider is not None:
            game_profile["lightning_setting_slider"] = [
                int(x) for x in slider.text.split(" ")
            ]

        light = lightning_setting.find("light")
        if light is not None:
            game_profile["lightning_setting_light"] = [
                int(x) for x in light.text.split(" ")
            ]

        concentration = lightning_setting.find("concentration")
        if concentration is not None:
            game_profile["lightning_setting_concentration"] = int(concentration.text)

    music_memo = request_info["root"][0].find("music_memo")
    if music_memo is not None:
        folders = music_memo.findall("folder")
        for f in folders:
            fi = f.attrib["folder_id"]
            fn = f.attrib["name"]
            ps = f.attrib["play_style"]
            mids = [int(x) for x in f.find("music_id").text.split(" ")]
            game_profile[f"music_memo_{fi}_{ps}_name"] = fn
            game_profile[f"music_memo_{fi}_{ps}_mids"] = mids

    # lightning_customize_flg = request_info["root"][0].find("lightning_customize_flg")
    # if lightning_customize_flg is not None:
    #    for k in [
    #        "flg_skin_0",
    #    ]:
    #        game_profile["lightning_setting_" + k] = int(
    #            lightning_customize_flg.attrib[k]
    #        )

    secret = request_info["root"][0].find("secret")
    if secret is not None:
        for k in ["flg1", "flg2", "flg3", "flg4"]:
            flg = secret.find(k)
            if flg is not None:
                game_profile["secret_" + k] = [int(x) for x in flg.text.split(" ")]

    leggendaria = request_info["root"][0].find("leggendaria")
    if leggendaria is not None:
        for k in ["flg1"]:
            flg = leggendaria.find(k)
            if flg is not None:
                game_profile["leggendaria_" + k] = [int(x) for x in flg.text.split(" ")]

    step = request_info["root"][0].find("step")
    if step is not None:
        for k in [
            "dp_fluctuation",
            "dp_level",
            "dp_mplay",
            "enemy_damage",
            "enemy_defeat_flg",
            "mission_clear_num",
            "progress",
            "sp_fluctuation",
            "sp_level",
            "sp_mplay",
            "tips_read_list",
            "total_point",
        ]:
            game_profile["stepup_" + k] = int(step.attrib[k])

        is_track_ticket = step.find("is_track_ticket")
        if is_track_ticket is not None:
            game_profile["stepup_is_track_ticket"] = int(is_track_ticket.text)

    dj_ranks = request_info["root"][0].findall("dj_rank")
    dj_ranks = [] if dj_ranks is None else dj_ranks
    for dj_rank in dj_ranks:
        style = int(dj_rank.attrib["style"])

        rank = dj_rank.find("rank")
        game_profile["dj_rank_" + ["single", "double"][style] + "_rank"] = [
            int(x) for x in rank.text.split(" ")
        ]

        point = dj_rank.find("point")
        game_profile["dj_rank_" + ["single", "double"][style] + "_point"] = [
            int(x) for x in point.text.split(" ")
        ]

    skin_equips = request_info["root"][0].findall("skin_equip")
    skin_equips = [] if skin_equips is None else skin_equips
    skin = {
        1: "explosion",
        2: "explosion_size",
        3: "turntable",
        4: "judgestring",
        5: "note",
        6: "note_size",
        13: "sudden",
        14: "grapharea",
        15: "lift",
        16: "keybeam",
        17: "keybeam_size",
        18: "fullcombo",
    }
    for skin_equip in skin_equips:
        skin_id = int(skin_equip.attrib["skin_id"])
        if skin_id in skin:
            game_profile[skin[skin_id]] = int(skin_equip.attrib["skin_no"])

    tdjskin_equips = request_info["root"][0].findall("tdjskin_equip")
    tdjskin_equips = [] if tdjskin_equips is None else tdjskin_equips
    tdjskin = {
        0: "submonitor",
    }
    for tdjskin_equip in tdjskin_equips:
        skin_id = int(tdjskin_equip.attrib["skin_id"])
        if skin_id in tdjskin:
            game_profile[tdjskin[skin_id]] = int(tdjskin_equip.attrib["skin_no"])

    notes_radars = request_info["root"][0].findall("notes_radar")
    notes_radars = [] if notes_radars is None else notes_radars
    for notes_radar in notes_radars:
        style = int(notes_radar.attrib["style"])
        score = notes_radar.find("radar_score")
        game_profile["notes_radar_" + ["single", "double"][style]] = [
            int(x) for x in score.text.split(" ")
        ]

    achievements = request_info["root"][0].find("achievements")
    if achievements is not None:
        for k in [
            "last_weekly",
            "pack_comp",
            "pack_flg",
            "pack_id",
            "play_pack",
            "visit_flg",
            "weekly_num",
        ]:
            game_profile["achievements_" + k] = int(achievements.attrib[k])

        trophy = achievements.find("trophy")
        if trophy is not None:
            game_profile["achievements_trophy"] = [
                int(x) for x in trophy.text.split(" ")
            ]

    grade = request_info["root"][0].find("grade")
    if grade is not None:
        grade_values = []
        for g in grade.findall("g"):
            grade_values.append([int(x) for x in g.text.split(" ")])

        profile["grade_single"] = int(grade.attrib["sgid"])
        profile["grade_double"] = int(grade.attrib["dgid"])
        profile["grade_values"] = grade_values

    deller_amount = game_profile.get("deller", 0)
    deller = request_info["root"][0].find("deller")
    if deller is not None:
        deller_amount = int(deller.attrib["deller"])
    game_profile["deller"] = deller_amount

    language = request_info["root"][0].find("language_setting")
    if language is not None:
        language_value = int(language.attrib["language"])
        game_profile["language_setting"] = language_value

    game_profile["spnum"] = game_profile.get("spnum", 0) + (1 if clt == 0 else 0)
    game_profile["dpnum"] = game_profile.get("dpnum", 0) + (1 if clt == 1 else 0)

    if request_info["model"] == "TDJ":
        game_profile["lightning_play_data_spnum"] = game_profile.get(
            "lightning_play_data_spnum", 0
        ) + (1 if clt == 0 else 0)
        game_profile["lightning_play_data_dpnum"] = game_profile.get(
            "lightning_play_data_dpnum", 0
        ) + (1 if clt == 1 else 0)

    profile["version"][str(game_version)] = game_profile

    get_db().table("iidx_profile").upsert(profile, where("card") == cid)

    response = E.response(E.IIDX31pc(iidxid=xid, cltype=clt))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/visit")
async def iidx31pc_visit(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX31pc(
            aflg=1,
            anum=1,
            pflg=1,
            pnum=1,
            sflg=1,
            snum=1,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/reg")
async def iidx31pc_reg(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    cid = request_info["root"][0].attrib["cid"]
    name = request_info["root"][0].attrib["name"]
    pid = request_info["root"][0].attrib["pid"]

    db = get_db().table("iidx_profile")
    all_profiles_for_card = db.get(Query().card == cid)

    if all_profiles_for_card is None:
        all_profiles_for_card = {"card": cid, "version": {}}

    if "iidx_id" not in all_profiles_for_card:
        iidx_id = random.randint(10000000, 99999999)
        all_profiles_for_card["iidx_id"] = iidx_id

    all_profiles_for_card["version"][str(game_version)] = {
        "game_version": game_version,
        "djname": name,
        "region": int(pid),
        "head": 0,
        "hair": 0,
        "face": 0,
        "hand": 0,
        "body": 0,
        "frame": 0,
        "turntable": 0,
        "explosion": 0,
        "bgm": 0,
        "folder_mask": 0,
        "sudden": 0,
        "judge_pos": 0,
        "categoryvoice": 0,
        "note": 0,
        "fullcombo": 0,
        "keybeam": 0,
        "judgestring": 0,
        "soundpreview": 0,
        "grapharea": 0,
        "lift": 0,
        "effector_lock": 0,
        "effector_type": 0,
        "explosion_size": 0,
        "note_size": 0,
        "keybeam_size": 0,
        "submonitor": 0,
        "alternate_hcn": 0,
        "kokokara_start": 0,
        "d_auto_adjust": 0,
        "d_auto_scrach": 0,
        "d_camera_layout": 0,
        "d_classic_hispeed": 0,
        "d_disp_judge": 0,
        "d_exscore": 0,
        "d_gauge_disp": 0,
        "d_ghost_score": 0,
        "d_gno": 0,
        "d_graph_score": 0,
        "d_gtype": 0,
        "d_hispeed": 0.000000,
        "d_judge": 0,
        "d_judgeAdj": 0,
        "d_lane_brignt": 0,
        "d_liflen": 0,
        "d_notes": 0.000000,
        "d_opstyle": 0,
        "d_pace": 0,
        "d_sdlen": 0,
        "d_sdtype": 0,
        "d_sorttype": 0,
        "d_sub_gno": 0,
        "d_timing": 0,
        "d_timing_split": 0,
        "d_tsujigiri_disp": 0,
        "d_tune": 0,
        "d_visualization": 0,
        "dach": 0,
        "dp_opt": 0,
        "dp_opt2": 0,
        "dpnum": 0,
        "gpos": 0,
        "mode": 0,
        "ngrade": 0,
        "pmode": 0,
        "rtype": 0,
        "s_auto_adjust": 0,
        "s_auto_scrach": 0,
        "s_camera_layout": 0,
        "s_classic_hispeed": 0,
        "s_disp_judge": 0,
        "s_exscore": 0,
        "s_gauge_disp": 0,
        "s_ghost_score": 0,
        "s_gno": 0,
        "s_graph_score": 0,
        "s_gtype": 0,
        "s_hispeed": 0.000000,
        "s_judge": 0,
        "s_judgeAdj": 0,
        "s_lane_brignt": 0,
        "s_liflen": 0,
        "s_notes": 0.000000,
        "s_opstyle": 0,
        "s_pace": 0,
        "s_sdlen": 0,
        "s_sdtype": 0,
        "s_sorttype": 0,
        "s_sub_gno": 0,
        "s_timing": 0,
        "s_timing_split": 0,
        "s_tsujigiri_disp": 0,
        "s_tune": 0,
        "s_visualization": 0,
        "sach": 0,
        "sp_opt": 0,
        "spnum": 0,
        "deller": 0,
        # Step up mode
        "stepup_dp_fluctuation": 0,
        "stepup_dp_level": 0,
        "stepup_dp_mplay": 0,
        "stepup_enemy_damage": 0,
        "stepup_enemy_defeat_flg": 0,
        "stepup_mission_clear_num": 0,
        "stepup_progress": 0,
        "stepup_sp_fluctuation": 0,
        "stepup_sp_level": 0,
        "stepup_sp_mplay": 0,
        "stepup_tips_read_list": 0,
        "stepup_total_point": 0,
        "stepup_is_track_ticket": 0,
        # DJ Rank
        "dj_rank_single_rank": [0] * 15,
        "dj_rank_double_rank": [0] * 15,
        "dj_rank_single_point": [0] * 15,
        "dj_rank_double_point": [0] * 15,
        # Notes Radar
        "notes_radar_single": [0] * 6,
        "notes_radar_double": [0] * 6,
        # Grades
        "grade_single": -1,
        "grade_double": -1,
        "grade_values": [],
        # Achievements
        "achievements_trophy": [0] * 160,
        "achievements_last_weekly": 0,
        "achievements_pack_comp": 0,
        "achievements_pack_flg": 0,
        "achievements_pack_id": 0,
        "achievements_play_pack": 0,
        "achievements_visit_flg": 0,
        "achievements_weekly_num": 0,
        # Other
        "language_setting": 0,
        "movie_agreement": 0,
        "lightning_play_data_spnum": 0,
        "lightning_play_data_dpnum": 0,
        # Lightning model settings
        "lightning_setting_slider": [0] * 7,
        "lightning_setting_light": [1] * 10,
        "lightning_setting_concentration": 0,
        "lightning_setting_headphone_vol": 0,
        "lightning_setting_resistance_sp_left": 0,
        "lightning_setting_resistance_sp_right": 0,
        "lightning_setting_resistance_dp_left": 0,
        "lightning_setting_resistance_dp_right": 0,
        "lightning_setting_skin_0": 0,
        "lightning_setting_flg_skin_0": 0,
        # Web UI/Other options
        "_show_category_grade": 0,
        "_show_category_status": 1,
        "_show_category_difficulty": 1,
        "_show_category_alphabet": 1,
        "_show_category_rival_play": 0,
        "_show_category_rival_winlose": 1,
        "_show_category_all_rival_play": 0,
        "_show_category_arena_winlose": 1,
        "_show_rival_shop_info": 1,
        "_hide_play_count": 0,
        "_show_score_graph_cutin": 1,
        "_hide_iidx_id": 0,
        "_classic_hispeed": 0,
        "_beginner_option_swap": 1,
        "_show_lamps_as_no_play_in_arena": 0,
        "skin_customize_flag_frame": 0,
        # "skin_customize_flag_turntable": 0,
        # "skin_customize_flag_bomb": 0,
        "skin_customize_flag_bgm": 0,
        "skin_customize_flag_lane": 0,
        # "skin_customize_flag_lane0": 0,
        # "skin_customize_flag_lane1": 0,
        # "skin_customize_flag_lane2": 0,
        # "skin_customize_flag_lane3": 0,
        # "skin_customize_flag_lane4": 0,
        # "skin_customize_flag_lane5": 0,
        # "skin_customize_flag_notes": 0,
        # "skin_customize_flag_fullcombo": 0,
        # "skin_customize_flag_keybeam": 0,
        # "skin_customize_flag_judgestring": 0,
        # "skin_customize_flag_bgm": 0,
        # "skin_customize_flag_lane": 0,
        # Rivals
        "sp_rival_1_iidx_id": 0,
        "sp_rival_2_iidx_id": 0,
        "sp_rival_3_iidx_id": 0,
        "sp_rival_4_iidx_id": 0,
        "sp_rival_5_iidx_id": 0,
        "sp_rival_6_iidx_id": 0,
        "dp_rival_1_iidx_id": 0,
        "dp_rival_2_iidx_id": 0,
        "dp_rival_3_iidx_id": 0,
        "dp_rival_4_iidx_id": 0,
        "dp_rival_5_iidx_id": 0,
        "dp_rival_6_iidx_id": 0,
    }
    db.upsert(all_profiles_for_card, where("card") == cid)

    card, card_split = get_id_from_profile(cid)

    response = E.response(E.IIDX31pc(id=card, id_str=card_split))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/getLaneGachaTicket")
async def iidx31pc_getlanegachaticket(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX31pc(
            *[
                E.ticket(
                    ticket_id=i,
                    arrange_id=i,
                    expire_date=0,
                )
                for i in range(5040)
            ],
            E.setting(
                sp=-1,
                dp_left=-1,
                dp_right=-1,
            ),
            E.info(
                last_page=1,
            ),
            E.free(
                num=10,
            ),
            E.favorite(
                arrange=1234567,
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/consumeLaneGachaTicket")
async def iidx31pc_consumelanegachaticket(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX31pc())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/drawLaneGacha")
async def iidx31pc_drawlanegacha(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX31pc(
            E.ticket(
                ticket_id=1,
                arrange_id=1,
                expire_date=0,
            ),
            E.session(session_id=1),
            status=0,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/eaappliresult")
async def iidx31pc_eaappliresult(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX31pc())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/logout")
async def iidx31pc_logout(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX31pc())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX31pc/getCompeInfo")
async def iidx31pc_getcompeinfo(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX31pc())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
