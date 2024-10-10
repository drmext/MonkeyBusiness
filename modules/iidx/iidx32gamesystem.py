from time import time

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["LDJ"]


@router.post("/{gameinfo}/IIDX32gameSystem/systemInfo")
async def iidx32gamesystem_systeminfo(request: Request):
    request_info = await core_process_request(request)

    unlock = ()
    # force unlock LM exclusives to complete unlock all songs server side
    # this makes LM exclusive folder disappear, so just use hex edits
    # unlock = (30106, 31084, 30077, 31085, 30107, 30028, 30076, 31083, 30098)

    current_time = round(time())

    response = E.response(
        E.IIDX32gameSystem(
            # E.option_2pp(),
            *[
                E.music_open(
                    E.music_id(mid, __type="s32"),
                    E.kind(0, __type="s32"),
                )
                for mid in unlock
            ],
            E.grade_course(
                E.play_style(0, __type="s32"),
                E.grade_id(15, __type="s32"),
                E.music_id_0(25090, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(23068, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(19004, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(29045, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.grade_course(
                E.play_style(0, __type="s32"),
                E.grade_id(16, __type="s32"),
                E.music_id_0(23005, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(27078, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(22065, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(27060, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.grade_course(
                E.play_style(0, __type="s32"),
                E.grade_id(17, __type="s32"),
                E.music_id_0(29007, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(26108, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(19002, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(18004, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.grade_course(
                E.play_style(0, __type="s32"),
                E.grade_id(18, __type="s32"),
                E.music_id_0(25007, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(18032, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(16020, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(12004, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.grade_course(
                E.play_style(1, __type="s32"),
                E.grade_id(15, __type="s32"),
                E.music_id_0(15032, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(29033, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(27092, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(30020, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.grade_course(
                E.play_style(1, __type="s32"),
                E.grade_id(16, __type="s32"),
                E.music_id_0(10028, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(26070, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(28091, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(23075, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.grade_course(
                E.play_style(1, __type="s32"),
                E.grade_id(17, __type="s32"),
                E.music_id_0(26012, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(28002, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(17017, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(28005, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.grade_course(
                E.play_style(1, __type="s32"),
                E.grade_id(18, __type="s32"),
                E.music_id_0(28008, __type="s32"),
                E.class_id_0(3, __type="s32"),
                E.music_id_1(15001, __type="s32"),
                E.class_id_1(3, __type="s32"),
                E.music_id_2(19002, __type="s32"),
                E.class_id_2(3, __type="s32"),
                E.music_id_3(9028, __type="s32"),
                E.class_id_3(3, __type="s32"),
                E.is_valid(1, __type="bool"),
            ),
            E.isNewSongAnother12OpenFlg(val=1),
            E.OldBPLBattleOpenPhase(val=3),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
