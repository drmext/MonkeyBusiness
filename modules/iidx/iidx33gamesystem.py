from time import time

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["LDJ"]


@router.post("/{gameinfo}/IIDX33gameSystem/systemInfo")
async def iidx33gamesystem_systeminfo(request: Request):
    request_info = await core_process_request(request)

    unlock = ()
    # force unlock LM exclusives to complete unlock all songs server side
    # this makes LM exclusive folder disappear, so just use hex edits
    # unlock = (30106, 31084, 30077, 31085, 30107, 30028, 30076, 31083, 30098)

    current_time = round(time())

    response = E.response(
        E.IIDX33gameSystem(
            # E.option_2pp(),
            *[
                E.music_open(
                    E.music_id(mid, __type="s32"),
                    E.kind(0, __type="s32"),
                )
                for mid in unlock
            ],
            #E.grade_course(
            #    E.play_style(0, __type="s32"),
            #    E.grade_id(15, __type="s32"),
            #    E.music_id_0(19022, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(23068, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(27013, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(29045, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.grade_course(
            #    E.play_style(0, __type="s32"),
            #    E.grade_id(16, __type="s32"),
            #    E.music_id_0(27034, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(24023, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(16009, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(25085, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.grade_course(
            #    E.play_style(0, __type="s32"),
            #    E.grade_id(17, __type="s32"),
            #    E.music_id_0(26087, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(19002, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(29050, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(30024, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.grade_course(
            #    E.play_style(0, __type="s32"),
            #    E.grade_id(18, __type="s32"),
            #    E.music_id_0(30052, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(18032, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(16020, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(12004, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.grade_course(
            #    E.play_style(1, __type="s32"),
            #    E.grade_id(15, __type="s32"),
            #    E.music_id_0(12002, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(31063, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(23046, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(30020, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.grade_course(
            #    E.play_style(1, __type="s32"),
            #    E.grade_id(16, __type="s32"),
            #    E.music_id_0(26106, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(14021, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(29052, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(23075, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.grade_course(
            #    E.play_style(1, __type="s32"),
            #    E.grade_id(17, __type="s32"),
            #    E.music_id_0(29042, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(26043, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(17017, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(28005, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.grade_course(
            #    E.play_style(1, __type="s32"),
            #    E.grade_id(18, __type="s32"),
            #    E.music_id_0(25007, __type="s32"),
            #    E.class_id_0(3, __type="s32"),
            #    E.music_id_1(29017, __type="s32"),
            #    E.class_id_1(3, __type="s32"),
            #    E.music_id_2(19002, __type="s32"),
            #    E.class_id_2(3, __type="s32"),
            #    E.music_id_3(9028, __type="s32"),
            #    E.class_id_3(3, __type="s32"),
            #    E.is_valid(1, __type="bool"),
            #),
            #E.arena_schedule(
            #    E.season(1, __type="u8"),
            #    E.phase(4, __type="u8"),
            #    E.rule_type(0, __type="u8"),
            #    E.start(current_time - 600, __type="u32"),
            #    E.end(current_time + 600, __type="u32"),
            #),
            #*[
            #    E.arena_reward(
            #        E.index(unlock.index(mid), __type="s32"),
            #        E.cube_num((unlock.index(mid) + 1) * 50, __type="s32"),
            #        E.kind(0, __type="s32"),
            #        E.value(mid, __type="str"),
            #    )
            #    for mid in unlock
            #],
            #*[
            #    E.arena_music_difficult(
            #        E.play_style(sp_dp, __type="s32"),
            #        E.arena_class(arena_class, __type="s32"),
            #        E.low_difficult(8, __type="s32"),
            #        E.high_difficult(12, __type="s32"),
            #        E.is_leggendaria(1, __type="bool"),
            #        E.force_music_list_id(0, __type="s32"),
            #    )
            #    for sp_dp in (0, 1)
            #    for arena_class in range(20)
            #],
            #*[
            #    E.arena_cpu_define(
            #        E.play_style(sp_dp, __type="s32"),
            #        E.arena_class(arena_class, __type="s32"),
            #        E.grade_id(18, __type="s32"),
            #        E.low_music_difficult(8, __type="s32"),
            #        E.high_music_difficult(12, __type="s32"),
            #        E.is_leggendaria(0, __type="bool"),
            #    )
            #    for sp_dp in (0, 1)
            #    for arena_class in range(20)
            #],
            #*[
            #    E.maching_class_range(
            #        E.play_style(sp_dp, __type="s32"),
            #        E.matching_class(arena_class, __type="s32"),
            #        E.low_arena_class(arena_class, __type="s32"),
            #        E.high_arena_class(arena_class, __type="s32"),
            #    )
            #    for sp_dp in (0, 1)
            #    for arena_class in range(20)
            #],
            #E.Event1Phase(val=0),
            E.isNewSongAnother12OpenFlg(val=1),
            #E.isKiwamiOpenFlg(val=1),
            #E.WorldTourismOpenList(val=-1),
            E.OldBPLBattleOpenPhase(val=1),
            #E.BPLBattleOpenPhase(val=3),
            E.beat(val=0),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
