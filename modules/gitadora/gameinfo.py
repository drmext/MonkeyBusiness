import time

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["M32"]


@router.post("/{gameinfo}/{ver}_gameinfo/get")
async def gitadora_gameinfo_get(ver: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    response = E.response(
        E(
            f"{ver}_gameinfo",
            E.now_date(round(time.time()), __type="u64"),
            E.extra(
                E.extra_lv(0, __type="s32" if game_version >= 10 else "u8"),
                E.extramusic(
                    E.music(
                        E.musicid(0, __type="s32"),
                        E.get_border(0, __type="u8"),
                    ),
                ),
            ),
            E.general_term(
                *[
                    E.termdata(
                        E.type(f"general_{s}", __type="str"),
                        E.term(1, __type="s32" if game_version >= 10 else "u8"),
                        E.start_date_ms(0, __type="u64"),
                        E.end_date_ms(0, __type="u64"),
                    )
                    for s in [
                        "ultimate_mobile_2019_info",
                        "50th_konami_logo",
                        "cardconnect_champ",
                        "otobear_birthday",
                        "kac_9th_info",
                        "floor_break_info",
                    ]
                ],
            ),
            *[
                E(
                    x,
                    E.term(1, __type="u8"),
                    E.start_date_ms(0, __type="u64"),
                    E.end_date_ms(0, __type="u64"),
                )
                for x in [
                    "phrase_combo_challenge",
                    "sdvx_stamprally3",
                    "chronicle_1",
                    "paseli_point_lottery",
                ]
            ],
            *[
                E(
                    f"phrase_combo_challenge_{x}",
                    E.term(1, __type="u8"),
                    E.start_date_ms(0, __type="u64"),
                    E.end_date_ms(0, __type="u64"),
                )
                for x in range(2, 21)
            ],
            E.long_otobear_fes_1(
                E.term(1, __type="u8"),
                E.start_date_ms(0, __type="u64"),
                E.end_date_ms(0, __type="u64"),
                E.bonus_musicid(),
            ),
            E.monstar_subjugation(
                E.bonus_musicid(0, __type="s32"),
                *[
                    E(
                        f"monstar_subjugation_{x}",
                        E.term(1, __type="u8"),
                        E.start_date_ms(0, __type="u64"),
                        E.end_date_ms(0, __type="u64"),
                    )
                    for x in range(1, 5)
                ],
            ),
            E.bear_fes(
                *[
                    E(
                        f"bear_fes_{x}",
                        E.term(1, __type="u8"),
                        E.start_date_ms(0, __type="u64"),
                        E.end_date_ms(0, __type="u64"),
                    )
                    for x in range(1, 5)
                ],
            ),
            *[
                E(
                    f"kouyou_challenge_{x}",
                    E.term(0, __type="u8"),
                    E.bonus_musicid(0, __type="s32"),
                )
                for x in range(1, 4)
            ],
            *[
                E(
                    x,
                    E.term(1, __type="u8"),
                    E.start_date_ms(0, __type="u64"),
                    E.end_date_ms(0, __type="u64"),
                    E.box_term(
                        E.state(0, __type="u8"),
                    ),
                )
                for x in ["thanksgiving", "lotterybox"]
            ],
            E.sticker_campaign(
                E.term(0, __type="u8"),
                E.sticker_list(),
            ),
            E.infect_music(
                E.term(1, __type="u8"),
            ),
            E.unlock_challenge(
                E.term(0, __type="s32" if game_version >= 10 else "u8"),
            ),
            E.battle(
                E.term(1, __type="s32" if game_version >= 10 else "u8"),
            ),
            E.battle_chara(
                E.term(1, __type="s32" if game_version >= 10 else "u8"),
            ),
            E.data_ver_limit(
                E.term(0, __type="s32" if game_version >= 9 else "u8"),
            ),
            E.ea_pass_propel(
                E.term(0, __type="s32" if game_version >= 10 else "u8"),
            ),
            E.monthly_skill(
                E.term(0, __type="u8"),
                E.target_music(
                    E.music(
                        E.musicid(0, __type="s32"),
                    ),
                ),
            ),
            E.update_prog(
                E.term(0, __type="s32" if game_version >= 10 else "u8"),
            ),
            E.rockwave(E.event_list()),
            E.livehouse(
                E.event_list(),
                E.bonus(
                    E.term(0, __type="u8"),
                    E.stage_bonus(0, __type="s32"),
                    E.charm_bonus(0, __type="s32"),
                    E.start_date_ms(0, __type="u64"),
                    E.end_date_ms(0, __type="u64"),
                ),
            ),
            E.general_term(),
            E.jubeat_omiyage_challenge(),
            E.kac2017(),
            E.nostalgia_concert(),
            E.trbitemdata(),
            E.ctrl_movie(),
            E.ng_jacket(),
            E.ng_recommend_music(),
            E.ranking(
                E.skill_0_999(),
                E.skill_1000_1499(),
                E.skill_1500_1999(),
                E.skill_2000_2499(),
                E.skill_2500_2999(),
                E.skill_3000_3499(),
                E.skill_3500_3999(),
                E.skill_4000_4499(),
                E.skill_4500_4999(),
                E.skill_5000_5499(),
                E.skill_5500_5999(),
                E.skill_6000_6499(),
                E.skill_6500_6999(),
                E.skill_7000_7499(),
                E.skill_7500_7999(),
                E.skill_8000_8499(),
                E.skill_8500_9999(),
                E.total(),
                E.original(),
                E.bemani(),
                E.famous(),
                E.anime(),
                E.band(),
                E.western(),
            ),
            E.processing_report_state(0, __type="u8"),
            E.assert_report_state(0, __type="u8"),
            E.recommendmusic(
                E.music(
                    E.musicid(0, __type="s32"),
                ),
                nr=1,
            ),
            E.demomusic(nr=0),
            E.event_skill(),
            E.temperature(
                E.is_send(0, __type="bool"),
            ),
            E.bemani_summer_2018(
                E.is_open(0, __type="bool"),
            ),
            E.kac2018(
                E.event(
                    E.term(0, __type="s32"),
                    E.since(0, __type="u64"),
                    E.till(0, __type="u64"),
                    E.is_open(0, __type="bool"),
                    E.target_music(
                        E.music_id([0] * 6, __type="s32"),
                    ),
                ),
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
