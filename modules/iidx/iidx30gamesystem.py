from time import time

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["LDJ"]


@router.post("/{gameinfo}/IIDX30gameSystem/systemInfo")
async def iidx30gamesystem_systeminfo(request: Request):
    request_info = await core_process_request(request)

    unlock = ()
    # force unlock LM exclusives to complete unlock all songs server side
    # this makes LM exclusive folder disappear, so just use hex edits
    # unlock = (28073, 28008, 29095, 29094, 29027, 30077, 30076, 30098, 30106, 30107, 30028, 30064, 30027)

    current_time = round(time())

    response = E.response(
        E.IIDX30gameSystem(
            *[
                E.music_open(
                    E.music_id(mid, __type="s32"),
                    E.kind(0, __type="s32"),
                )
                for mid in unlock
            ],
            E.arena_schedule(
                E.phase(3, __type="u8"),
                E.start(current_time - 600, __type="u32"),
                E.end(current_time + 600, __type="u32"),
            ),
            *[
                E.arena_reward(
                    E.index(unlock.index(mid), __type="s32"),
                    E.cube_num((unlock.index(mid) + 1) * 50, __type="s32"),
                    E.kind(0, __type="s32"),
                    E.value(mid, __type="str"),
                )
                for mid in unlock
            ],
            *[
                E.arena_music_difficult(
                    E.play_style(sp_dp, __type="s32"),
                    E.arena_class(arena_class, __type="s32"),
                    E.low_difficult(8, __type="s32"),
                    E.high_difficult(12, __type="s32"),
                    E.is_leggendaria(1, __type="bool"),
                    E.force_music_list_id(0, __type="s32"),
                )
                for sp_dp in (0, 1)
                for arena_class in range(20)
            ],
            *[
                E.arena_cpu_define(
                    E.play_style(sp_dp, __type="s32"),
                    E.arena_class(arena_class, __type="s32"),
                    E.grade_id(18, __type="s32"),
                    E.low_music_difficult(8, __type="s32"),
                    E.high_music_difficult(12, __type="s32"),
                    E.is_leggendaria(0, __type="bool"),
                )
                for sp_dp in (0, 1)
                for arena_class in range(20)
            ],
            *[
                E.maching_class_range(
                    E.play_style(sp_dp, __type="s32"),
                    E.matching_class(arena_class, __type="s32"),
                    E.low_arena_class(arena_class, __type="s32"),
                    E.high_arena_class(arena_class, __type="s32"),
                )
                for sp_dp in (0, 1)
                for arena_class in range(20)
            ],
            E.CommonBossPhase(val=0),
            E.Event1InternalPhase(val=0),
            E.ExtraBossEventPhase(val=0),
            E.isNewSongAnother12OpenFlg(val=1),
            E.gradeOpenPhase(val=2),
            E.isEiseiOpenFlg(val=1),
            E.WorldTourismOpenList(val=-1),
            E.BPLBattleOpenPhase(val=3),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
