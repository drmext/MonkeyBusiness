from time import time

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["LDJ"]


@router.post("/{gameinfo}/IIDX30gameSystem/systemInfo")
async def iidx30gamesystem_systeminfo(request: Request):
    request_info = await core_process_request(request)

    unlock = ()  # (28008, 28065, 28073, 28088, 28089, 29027, 29094, 29095)
    sp_dp = (0, 1)

    response = E.response(
        E.IIDX30gameSystem(
            E.arena_schedule(
                E.phase(3, __type="u8"),
                E.start(1605784800, __type="u32"),
                E.end(round(time()), __type="u32"),
            ),
            E.CommonBossPhase(val=0),
            E.Event1InternalPhase(val=0),
            E.ExtraBossEventPhase(val=0),
            E.isNewSongAnother12OpenFlg(val=1),
            E.gradeOpenPhase(val=2),
            E.isEiseiOpenFlg(val=1),
            E.WorldTourismOpenList(val=1),
            E.BPLBattleOpenPhase(val=2),
            *[
                E.music_open(
                    E.music_id(s, __type="s32"),
                    E.kind(0, __type="s32"),
                )
                for s in unlock
            ],
            *[
                E.arena_reward(
                    E.index(unlock.index(s), __type="s32"),
                    E.cube_num((unlock.index(s) + 1) * 50, __type="s32"),
                    E.kind(0, __type="s32"),
                    E.value(s, __type="str"),
                )
                for s in unlock
            ],
            *[
                E.arena_music_difficult(
                    E.play_style(s, __type="s32"),
                    E.arena_class(19, __type="s32"),
                    E.low_difficult(8, __type="s32"),
                    E.high_difficult(12, __type="s32"),
                    E.is_leggendaria(1, __type="bool"),
                    E.force_music_list_id(0, __type="s32"),
                )
                for s in sp_dp
            ],
            *[
                E.arena_cpu_define(
                    E.play_style(s, __type="s32"),
                    E.arena_class(19, __type="s32"),
                    E.grade_id(18, __type="s32"),
                    E.low_music_difficult(8, __type="s32"),
                    E.high_music_difficult(12, __type="s32"),
                    E.is_leggendaria(0, __type="bool"),
                )
                for s in sp_dp
            ],
            *[
                E.maching_class_range(
                    E.play_style(s[0], __type="s32"),
                    E.matching_class(s[1], __type="s32"),
                    E.low_arena_class(0, __type="s32"),
                    E.high_arena_class(19, __type="s32"),
                )
                for s in ((0, 2), (0, 1), (1, 2), (1, 1))
            ],
            *[
                E.arena_force_music(
                    E.play_style(s, __type="s32"),
                    E.force_music_list_id(0, __type="s32"),
                    E.index(0, __type="s32"),
                    E.music_id(1000, __type="s32"),
                    E.note_grade(0, __type="s32"),
                    E.is_active(0, __type="bool"),
                )
                for s in sp_dp
            ],
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
