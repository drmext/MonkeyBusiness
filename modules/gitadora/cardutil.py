from tinydb import Query, where

import random

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


@router.post("/{gameinfo}/{ver}_cardutil/check")
async def gitadora_cardutil_check(ver: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    data = request_info["root"][0].find("player")

    no = int(data.attrib["no"])

    dataid = data.find("refid").text

    profile = get_game_profile(dataid, game_version)

    if profile is None:
        state = 0
        name = ""
        did = 0
    else:
        state = 2
        name = profile["name"]
        did = 1

    response = E.response(
        E(
            f"{ver}_cardutil",
            E.player(
                E.name(name, __type="str"),
                E.charaid(0, __type="s32"),
                E.did(did, __type="s32"),
                E.skilldata(
                    E.skill(0, __type="s32"),
                    E.all_skill(0, __type="s32"),
                    E.old_skill(0, __type="s32"),
                    E.old_all_skill(0, __type="s32"),
                ),
                no=1,
                state=state,
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/{ver}_cardutil/regist")
async def gitadora_cardutil_regist(ver: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]
    spec = request_info["spec"]

    data = request_info["root"][0].find("player")

    no = int(data.attrib["no"])

    dataid = data.find("refid").text

    db = get_db().table("gitadora_profile")
    all_profiles_for_card = db.get(Query().card == dataid)

    if "gitadora_id" not in all_profiles_for_card:
        gitadora_id = random.randint(10000000, 99999999)
        all_profiles_for_card["gitadora_id"] = gitadora_id

    all_profiles_for_card["version"][str(game_version)] = {
        "game_version": game_version,
        "name": "kors k",
        "title": "MONKEY BUSINESS",
        "charaid": 0,
        "stickers": {},
    }

    for game_type in ("drummania", "guitarfreaks"):
        all_profiles_for_card["version"][str(game_version)][game_type] = {
            "customdata_playstyle": [
                0,
                1,
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
                0,
                0,
                0,
                0,
                20,
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
                0,
                20,
                0,
            ],
            "customdata_custom": [0] * 50,
            "playinfo_cabid": 1,
            "playinfo_play": 0,
            "playinfo_playtime": 0,
            "playinfo_playterm": 0,
            "playinfo_session_cnt": 0,
            "playinfo_saved_cnt": 0,
            "playinfo_matching_num": 0,
            "playinfo_extra_stage": 0,
            "playinfo_extra_play": 0,
            "playinfo_extra_clear": 0,
            "playinfo_encore_play": 0,
            "playinfo_encore_clear": 0,
            "playinfo_pencore_play": 0,
            "playinfo_pencore_clear": 0,
            "playinfo_max_clear_diff": 0,
            "playinfo_max_full_diff": 0,
            "playinfo_max_exce_diff": 0,
            "playinfo_clear_num": 0,
            "playinfo_full_num": 0,
            "playinfo_exce_num": 0,
            "playinfo_no_num": 0,
            "playinfo_e_num": 0,
            "playinfo_d_num": 0,
            "playinfo_c_num": 0,
            "playinfo_b_num": 0,
            "playinfo_a_num": 0,
            "playinfo_s_num": 0,
            "playinfo_ss_num": 0,
            "playinfo_last_category": 0,
            "playinfo_last_musicid": 0,
            "playinfo_last_seq": 0,
            "playinfo_disp_level": 0,
            "tutorial_progress": 0,
            "tutorial_disp_state": 0,
            "information": [0] * 50,
            "reward": [0] * 50,
            "skilldata_skill": 0,
            "skilldata_allskill": 0,
            "groove_extra_gauge": 0,
            "groove_encore_gauge": 0,
            "groove_encore_cnt": 0,
            "groove_encore_success": 0,
            "groove_unlock_point": 0,
            "record_max_skill": 0,
            "record_max_all_skill": 0,
            "record_max_clear_diff": 0,
            "record_max_full_diff": 0,
            "record_max_exce_diff": 0,
            "record_max_clear_music_num": 0,
            "record_max_full_music_num": 0,
            "record_max_exce_music_num": 0,
            "record_max_clear_seq_num": 0,
            "record_max_classic_all_skill": 0,
            "record_diff_100_nr": 0,
            "record_diff_150_nr": 0,
            "record_diff_200_nr": 0,
            "record_diff_250_nr": 0,
            "record_diff_300_nr": 0,
            "record_diff_350_nr": 0,
            "record_diff_400_nr": 0,
            "record_diff_450_nr": 0,
            "record_diff_500_nr": 0,
            "record_diff_550_nr": 0,
            "record_diff_600_nr": 0,
            "record_diff_650_nr": 0,
            "record_diff_700_nr": 0,
            "record_diff_750_nr": 0,
            "record_diff_800_nr": 0,
            "record_diff_850_nr": 0,
            "record_diff_900_nr": 0,
            "record_diff_950_nr": 0,
            "record_diff_100_clear": [0] * 7,
            "record_diff_150_clear": [0] * 7,
            "record_diff_200_clear": [0] * 7,
            "record_diff_250_clear": [0] * 7,
            "record_diff_300_clear": [0] * 7,
            "record_diff_350_clear": [0] * 7,
            "record_diff_400_clear": [0] * 7,
            "record_diff_450_clear": [0] * 7,
            "record_diff_500_clear": [0] * 7,
            "record_diff_550_clear": [0] * 7,
            "record_diff_600_clear": [0] * 7,
            "record_diff_650_clear": [0] * 7,
            "record_diff_700_clear": [0] * 7,
            "record_diff_750_clear": [0] * 7,
            "record_diff_800_clear": [0] * 7,
            "record_diff_850_clear": [0] * 7,
            "record_diff_900_clear": [0] * 7,
            "record_diff_950_clear": [0] * 7,
            "favorite_music_list_1": [-1] * 100,
            "favorite_music_list_2": [-1] * 100,
            "favorite_music_list_3": [-1] * 100,
            "recommend_musicid_list": [-1] * 5,
            "thanks_medal_medal": 0,
            "thanks_medal_granted_total_medal": 0,
            # "skindata_skin": [0] * 100,
        }

    db.upsert(all_profiles_for_card, where("card") == dataid)

    response = E.response(
        E(
            f"{ver}_cardutil",
            E.player(
                E.is_succession(0, __type="bool"),
                E.did(1, __type="s32"),
                no=no,
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
