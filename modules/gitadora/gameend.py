from tinydb import Query, where

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["M32", "L33", "L32", "K33", "K32", "J33", "J32"]


def get_profile(cid):
    return get_db().table("gitadora_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


@router.post("/{gameinfo}/{ver}_gameend/regist")
async def gitadora_gameend_regist(ver: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]
    spec = request_info["spec"]

    if spec == "A":
        g = "guitarfreaks"
    elif spec == "B":
        g = "drummania"
    elif spec == "C":
        g = "guitarfreaksdelta"
    elif spec == "D":
        g = "drummaniadelta"

    root = request_info["root"][0]

    players = root.findall("player")

    for player in players:
        no = int(player.attrib["no"])

        if player.attrib["card"] != "use":
            continue

        dataid = player.find("refid").text
        profile = get_profile(dataid)
        gitadora_id = profile["gitadora_id"]
        game_profile = profile["version"].get(str(game_version), {})

        game_profile[g]["customdata_playstyle"] = [
            int(x) for x in player.find("customdata/playstyle").text.split(" ")
        ]
        game_profile[g]["customdata_custom"] = [
            int(x) for x in player.find("customdata/custom").text.split(" ")
        ]

        for k in [
            "cabid",
            "play",
            "playtime",
            "playterm",
            "session_cnt",
            "matching_num",
            "extra_stage",
            "extra_play",
            "extra_clear",
            "encore_play",
            "encore_clear",
            "pencore_play",
            "pencore_clear",
            "max_clear_diff",
            "max_full_diff",
            "max_exce_diff",
            "clear_num",
            "full_num",
            "exce_num",
            "no_num",
            "e_num",
            "d_num",
            "c_num",
            "b_num",
            "a_num",
            "s_num",
            "ss_num",
            "last_category",
            "last_musicid",
            "last_seq",
            "disp_level",
        ]:
            game_profile[g]["playinfo_" + k] = int(player.find(f"playinfo/{k}").text)

        game_profile[g]["tutorial_progress"] = int(
            player.find("tutorial/progress").text
        )
        game_profile[g]["tutorial_disp_state"] = int(
            player.find("tutorial/disp_state").text
        )

        game_profile[g]["information"] = [
            int(x) for x in player.find("information/info").text.split(" ")
        ]
        game_profile[g]["reward"] = [
            int(x) for x in player.find("reward/status").text.split(" ")
        ]

        game_profile[g]["skilldata_skill"] = int(player.find("skilldata/skill").text)
        game_profile[g]["skilldata_allskill"] = int(
            player.find("skilldata/all_skill").text
        )

        groove = [
            "extra_gauge",
            "encore_gauge",
            "encore_cnt",
            "encore_success",
        ]
        if game_version > 6:
            groove.append("unlock_point")

        for k in groove:
            game_profile[g]["groove_" + k] = int(player.find(f"groove/{k}").text)

        record_max = [
            "skill",
            "all_skill",
            "clear_diff",
            "full_diff",
            "exce_diff",
            "clear_music_num",
            "full_music_num",
            "exce_music_num",
            "clear_seq_num",
        ]
        if game_version > 6:
            record_max.append("classic_all_skill")

        for k in record_max:
            game_profile[g]["record_max_" + k] = int(
                player.find(f"record/max/{k}").text
            )

        for k in [
            "diff_100_nr",
            "diff_150_nr",
            "diff_200_nr",
            "diff_250_nr",
            "diff_300_nr",
            "diff_350_nr",
            "diff_400_nr",
            "diff_450_nr",
            "diff_500_nr",
            "diff_550_nr",
            "diff_600_nr",
            "diff_650_nr",
            "diff_700_nr",
            "diff_750_nr",
            "diff_800_nr",
            "diff_850_nr",
            "diff_900_nr",
            "diff_950_nr",
        ]:
            game_profile[g]["record_" + k] = int(player.find(f"record/diff/{k}").text)

        for k in [
            "diff_100_clear",
            "diff_150_clear",
            "diff_200_clear",
            "diff_250_clear",
            "diff_300_clear",
            "diff_350_clear",
            "diff_400_clear",
            "diff_450_clear",
            "diff_500_clear",
            "diff_550_clear",
            "diff_600_clear",
            "diff_650_clear",
            "diff_700_clear",
            "diff_750_clear",
            "diff_800_clear",
            "diff_850_clear",
            "diff_900_clear",
            "diff_950_clear",
        ]:
            game_profile[g]["record_" + k] = [
                int(x) for x in player.find(f"record/diff/{k}").text.split(" ")
            ]

        for k in [
            "music_list_1",
            "music_list_2",
            "music_list_3",
        ]:
            game_profile[g]["favorite_" + k] = [
                int(x) for x in player.find(f"favoritemusic/{k}").text.split(" ")
            ]

        profile["version"][str(game_version)] = game_profile

        get_db().table("gitadora_profile").upsert(profile, where("card") == dataid)

        stage = player.findall("stage")

        for s in stage:
            data_version = root.find("data_version").text
            timestamp = int(s.find("date_ms").text)
            musicid = int(s.find("musicid").text)
            seq = int(s.find("seq").text)
            skill = int(s.find("skill").text)
            new_skill = int(s.find("new_skill").text)
            clear = int(s.find("clear").text)
            auto_clear = int(s.find("auto_clear").text)
            fullcombo = int(s.find("fullcombo").text)
            excellent = int(s.find("excellent").text)
            medal = int(s.find("medal").text)
            perc = int(s.find("perc").text)
            new_perc = int(s.find("new_perc").text)
            rank = int(s.find("rank").text)
            score = int(s.find("score").text)
            combo = int(s.find("combo").text)
            max_combo_perc = int(s.find("max_combo_perc").text)
            flags = int(s.find("flags").text)
            phrase_combo_perc = int(s.find("phrase_combo_perc").text)
            perfect = int(s.find("perfect").text)
            great = int(s.find("great").text)
            good = int(s.find("good").text)
            ok = int(s.find("ok").text)
            miss = int(s.find("miss").text)
            perfect_perc = int(s.find("perfect_perc").text)
            great_perc = int(s.find("great_perc").text)
            good_perc = int(s.find("good_perc").text)
            ok_perc = int(s.find("ok_perc").text)
            miss_perc = int(s.find("miss_perc").text)
            meter = int(s.find("meter").text)
            meter_prog = int(s.find("meter_prog").text)
            before_meter = int(s.find("before_meter").text)
            before_meter_prog = int(s.find("before_meter_prog").text)
            is_new_meter = int(s.find("is_new_meter").text)
            phrase_data_num = int(s.find("phrase_data_num").text)
            phrase_addr = [int(x) for x in s.find("phrase_addr").text.split(" ")]
            phrase_type = [int(x) for x in s.find("phrase_type").text.split(" ")]
            phrase_status = [int(x) for x in s.find("phrase_status").text.split(" ")]
            phrase_end_addr = int(s.find("phrase_end_addr").text)

            get_db().table(f"{g}_scores").insert(
                {
                    "timestamp": timestamp,
                    "game_version": game_version,
                    "gitadora_id": gitadora_id,
                    "data_version": data_version,
                    "musicid": musicid,
                    "seq": seq,
                    "skill": skill,
                    "new_skill": new_skill,
                    "clear": clear,
                    "auto_clear": auto_clear,
                    "fullcombo": fullcombo,
                    "excellent": excellent,
                    "medal": medal,
                    "perc": perc,
                    "new_perc": new_perc,
                    "rank": rank,
                    "score": score,
                    "combo": combo,
                    "max_combo_perc": max_combo_perc,
                    "flags": flags,
                    "phrase_combo_perc": phrase_combo_perc,
                    "perfect": perfect,
                    "great": great,
                    "good": good,
                    "ok": ok,
                    "miss": miss,
                    "perfect_perc": perfect_perc,
                    "great_perc": great_perc,
                    "good_perc": good_perc,
                    "ok_perc": ok_perc,
                    "miss_perc": miss_perc,
                    "meter": meter,
                    "meter_prog": meter_prog,
                    "before_meter": before_meter,
                    "before_meter_prog": before_meter_prog,
                    "is_new_meter": is_new_meter,
                    "phrase_data_num": phrase_data_num,
                    "phrase_addr": phrase_addr,
                    "phrase_type": phrase_type,
                    "phrase_status": phrase_status,
                    "phrase_end_addr": phrase_end_addr,
                },
            )

            best_score = (
                get_db()
                .table(f"{g}_scores_best")
                .get(
                    (where("gitadora_id") == gitadora_id)
                    & (where("musicid") == musicid)
                    & (where("seq") == seq)
                )
            )
            best_score = {} if best_score is None else best_score

            best_perc = best_score.get("perc", perc)
            best_score_data = {
                "gitadora_id": gitadora_id,
                "musicid": musicid,
                "seq": seq,
                "skill": max(skill, best_score.get("skill", skill)),
                "clear": max(clear, best_score.get("clear", clear)),
                "fullcombo": max(fullcombo, best_score.get("fullcombo", fullcombo)),
                "excellent": max(excellent, best_score.get("excellent", excellent)),
                "perc": max(perc, best_score.get("perc", perc)),
                "rank": max(rank, best_score.get("rank", rank)),
                "meter": meter
                if perc >= best_perc
                else best_score.get("meter", meter),
                "meter_prog": meter_prog
                if perc >= best_perc
                else best_score.get("meter_prog", meter_prog),
            }

            get_db().table(f"{g}_scores_best").upsert(
                best_score_data,
                (where("gitadora_id") == gitadora_id)
                & (where("musicid") == musicid)
                & (where("seq") == seq),
            )

    response = E.response(
        E(
            f"{ver}_gameend",
            E.gamemode(mode="game_mode"),
            E.player(
                E.skill(
                    E.rank(1, __type="s32"),
                    E.total_nr(1, __type="s32"),
                ),
                E.all_skill(
                    E.rank(1, __type="s32"),
                    E.total_nr(1, __type="s32"),
                ),
                no=no,
                state=0,
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
