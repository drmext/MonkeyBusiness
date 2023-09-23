import random
import time

from tinydb import Query, where

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

from base64 import b64decode, b64encode

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["MDX"]


def get_profile(cid):
    return get_db().table("ddr_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


def get_common(ddr_id, game_version, idx):
    profile = get_db().table("ddr_profile").get(where("ddr_id") == int(ddr_id))
    if profile is not None:
        return profile["version"].get(str(game_version), None)["common"].split(",")[idx]
    else:
        return 0


@router.post("/{gameinfo}/playerdata/usergamedata_advanced")
async def playerdata_usergamedata_advanced(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]
    is_omni = True if request_info["rev"] == "O" else False
    response = None

    data = request_info["root"][0].find("data")
    mode = data.find("mode").text
    gamesession = data.find("gamesession").text
    refid = data.find("refid").text

    default = "X0000000000000000000000000000000"[: -len(gamesession)] + gamesession

    db = get_db()

    all_profiles_for_card = db.table("ddr_profile").get(Query().card == refid)

    if mode == "usernew":
        shoparea = data.find("shoparea").text

        if "ddr_id" not in all_profiles_for_card:
            ddr_id = random.randint(10000000, 99999999)
            all_profiles_for_card["ddr_id"] = ddr_id

        all_profiles_for_card["version"][str(game_version)] = {
            "game_version": game_version,
            "calories_disp": "Off",
            "character": "All Character Random",
            "arrow_skin": "Normal",
            "filter": "Darkest",
            "guideline": "Center",
            "priority": "Judgment",
            "timing_disp": "On",
            "rival_1_ddr_id": 0,
            "rival_2_ddr_id": 0,
            "rival_3_ddr_id": 0,
            "single_grade": 0,
            "double_grade": 0,
        }

        db.table("ddr_profile").upsert(all_profiles_for_card, where("card") == refid)

        response = E.response(
            E.playerdata(
                E.result(0, __type="s32"),
                E.seq("-".join([str(ddr_id)[:4], str(ddr_id)[4:]]), __type="str"),
                E.code(ddr_id, __type="s32"),
                E.shoparea(shoparea, __type="str"),
            )
        )

    elif mode == "userload" and refid != default:
        all_scores = {}
        if all_profiles_for_card is not None:
            ddr_id = all_profiles_for_card["ddr_id"]
            profile = get_game_profile(refid, game_version)

            single_grade = profile.get("single_grade", 0)
            double_grade = profile.get("double_grade", 0)

            for record in db.table("ddr_scores_best").search(
                (where("game_version") == game_version) & (where("ddr_id") == ddr_id)
            ):
                mcode = record["mcode"]
                difficulty = record["difficulty"]
                if mcode not in all_scores:
                    all_scores[mcode] = [[0, 0, 0, 0, 0] for x in range(10)]
                all_scores[mcode][difficulty] = [
                    1,
                    record["rank"],
                    record["lamp"],
                    record["score"],
                    record["ghostid"],
                ]

        response = E.response(
            E.playerdata(
                E.result(0, __type="s32"),
                E.is_new(1 if all_profiles_for_card is None else 0, __type="bool"),
                E.is_refid_locked(0, __type="bool"),
                E.eventdata_count_all(1, __type="s16"),
                *[
                    E.music(
                        E.mcode(int(mcode), __type="u32"),
                        *[
                            E.note(
                                E.count(s[0], __type="u16"),
                                E.rank(s[1], __type="u8"),
                                E.clearkind(s[2], __type="u8"),
                                E.score(s[3], __type="s32"),
                                E.ghostid(s[4], __type="s32"),
                            )
                            for s in [score for score in all_scores.get(mcode)]
                        ],
                    )
                    for mcode in all_scores.keys()
                ],
                *[
                    E.eventdata(
                        E.eventid(event, __type="u32"),
                        E.eventtype(9999, __type="s32"),
                        E.eventno(0, __type="u32"),
                        E.condition(0, __type="s64"),
                        E.reward(0, __type="u32"),
                        E.comptime(1, __type="s32"),
                        E.savedata(0, __type="s64"),
                    )
                    for event in [
                        e for e in range(1, 100) if e not in [4, 6, 7, 8, 14, 47]
                    ]
                ],
                E.grade(
                    E.single_grade(single_grade, __type="u32"),
                    E.double_grade(double_grade, __type="u32"),
                ),
                E.golden_league(
                    E.league_class(0, __type="s32"),
                    E.current(
                        E.id(0, __type="s32"),
                        E.league_name_base64("", __type="str"),
                        E.start_time(0, __type="u64"),
                        E.end_time(0, __type="u64"),
                        E.summary_time(0, __type="u64"),
                        E.league_status(0, __type="s32"),
                        E.league_class(0, __type="s32"),
                        E.league_class_result(0, __type="s32"),
                        E.ranking_number(0, __type="s32"),
                        E.total_exscore(0, __type="s32"),
                        E.total_play_count(0, __type="s32"),
                        E.join_number(0, __type="s32"),
                        E.promotion_ranking_number(0, __type="s32"),
                        E.demotion_ranking_number(0, __type="s32"),
                        E.promotion_exscore(0, __type="s32"),
                        E.demotion_exscore(0, __type="s32"),
                    ),
                ),
                E.championship(
                    E.championship_id(0, __type="s32"),
                    E.name_base64("", __type="str"),
                    E.lang(
                        E.destinationcodes("", __type="str"),
                        E.name_base64("", __type="str"),
                    ),
                    E.music(
                        E.mcode(0, __type="u32"),
                        E.notetype(0, __type="s8"),
                        E.playstyle(0, __type="s32"),
                    ),
                ),
                E.preplayable(),
            )
        )

    elif mode == "ghostload":
        ghostid = int(data.find("ghostid").text)
        record = db.table("ddr_scores").get(doc_id=ghostid)

        response = E.response(
            E.playerdata(
                E.result(0, __type="s32"),
                E.ghostdata(
                    E.code(record["ddr_id"], __type="s32"),
                    E.mcode(record["mcode"], __type="u32"),
                    E.notetype(record["difficulty"], __type="u8"),
                    E.ghostsize(record["ghostsize"], __type="s32"),
                    E.ghost(record["ghost"], __type="string"),
                ),
            )
        )

    elif mode == "usersave" and refid != default:
        timestamp = time.time()

        ddr_id = int(data.find("ddrcode").text)
        playstyle = int(data.find("playstyle").text)
        pcbid = data.find("pcbid").text
        shoparea = data.find("shoparea").text

        note = data.findall("note")

        if int(data.find("isgameover").text) == 0:
            for n in note:
                if int(n.find("stagenum").text) != 0:
                    mcode = int(n.find("mcode").text)
                    difficulty = int(n.find("notetype").text)
                    rank = int(n.find("rank").text)
                    lamp = int(n.find("clearkind").text)
                    score = int(n.find("score").text)
                    exscore = int(n.find("exscore").text)
                    maxcombo = int(n.find("maxcombo").text)
                    life = int(n.find("life").text)
                    fastcount = int(n.find("fastcount").text)
                    slowcount = int(n.find("slowcount").text)
                    judge_marvelous = int(n.find("judge_marvelous").text)
                    judge_perfect = int(n.find("judge_perfect").text)
                    judge_great = int(n.find("judge_great").text)
                    judge_good = int(n.find("judge_good").text)
                    judge_boo = int(n.find("judge_boo").text)
                    judge_miss = int(n.find("judge_miss").text)
                    judge_ok = int(n.find("judge_ok").text)
                    judge_ng = int(n.find("judge_ng").text)
                    calorie = int(n.find("calorie").text)
                    ghostsize = int(n.find("ghostsize").text)
                    ghost = n.find("ghost").text
                    opt_speed = int(n.find("opt_speed").text)
                    opt_boost = int(n.find("opt_boost").text)
                    opt_appearance = int(n.find("opt_appearance").text)
                    opt_turn = int(n.find("opt_turn").text)
                    opt_dark = int(n.find("opt_dark").text)
                    opt_scroll = int(n.find("opt_scroll").text)
                    opt_arrowcolor = int(n.find("opt_arrowcolor").text)
                    opt_cut = int(n.find("opt_cut").text)
                    opt_freeze = int(n.find("opt_freeze").text)
                    opt_jump = int(n.find("opt_jump").text)
                    opt_arrowshape = int(n.find("opt_arrowshape").text)
                    opt_filter = int(n.find("opt_filter").text)
                    opt_guideline = int(n.find("opt_guideline").text)
                    opt_gauge = int(n.find("opt_gauge").text)
                    opt_judgepriority = int(n.find("opt_judgepriority").text)
                    opt_timing = int(n.find("opt_timing").text)

            db.table("ddr_scores").insert(
                {
                    "timestamp": timestamp,
                    "pcbid": pcbid,
                    "shoparea": shoparea,
                    "game_version": game_version,
                    "ddr_id": ddr_id,
                    "playstyle": playstyle,
                    "mcode": mcode,
                    "difficulty": difficulty,
                    "rank": rank,
                    "lamp": lamp,
                    "score": score,
                    "exscore": exscore,
                    "maxcombo": maxcombo,
                    "life": life,
                    "fastcount": fastcount,
                    "slowcount": slowcount,
                    "judge_marvelous": judge_marvelous,
                    "judge_perfect": judge_perfect,
                    "judge_great": judge_great,
                    "judge_good": judge_good,
                    "judge_boo": judge_boo,
                    "judge_miss": judge_miss,
                    "judge_ok": judge_ok,
                    "judge_ng": judge_ng,
                    "calorie": calorie,
                    "ghostsize": ghostsize,
                    "ghost": ghost,
                    "opt_speed": opt_speed,
                    "opt_boost": opt_boost,
                    "opt_appearance": opt_appearance,
                    "opt_turn": opt_turn,
                    "opt_dark": opt_dark,
                    "opt_scroll": opt_scroll,
                    "opt_arrowcolor": opt_arrowcolor,
                    "opt_cut": opt_cut,
                    "opt_freeze": opt_freeze,
                    "opt_jump": opt_jump,
                    "opt_arrowshape": opt_arrowshape,
                    "opt_filter": opt_filter,
                    "opt_guideline": opt_guideline,
                    "opt_gauge": opt_gauge,
                    "opt_judgepriority": opt_judgepriority,
                    "opt_timing": opt_timing,
                },
            )

            best = db.table("ddr_scores_best").get(
                (where("ddr_id") == ddr_id)
                & (where("game_version") == game_version)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
            )
            best = {} if best is None else best

            best_score_data = {
                "game_version": game_version,
                "ddr_id": ddr_id,
                "playstyle": playstyle,
                "mcode": mcode,
                "difficulty": difficulty,
                "rank": min(rank, best.get("rank", rank)),
                "lamp": max(lamp, best.get("lamp", lamp)),
                "score": max(score, best.get("score", score)),
                "exscore": max(exscore, best.get("exscore", exscore)),
            }

            ghostid = db.table("ddr_scores").get(
                (where("ddr_id") == ddr_id)
                & (where("game_version") == game_version)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
                & (where("score") == max(score, best.get("score", score)))
            )
            best_score_data["ghostid"] = ghostid.doc_id

            db.table("ddr_scores_best").upsert(
                best_score_data,
                (where("ddr_id") == ddr_id)
                & (where("game_version") == game_version)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty),
            )

        elif int(data.find("isgameover").text) == 1:
            single_grade = int(data.find("grade/single_grade").text)
            double_grade = int(data.find("grade/double_grade").text)
            profile = get_profile(refid)
            game_profile = profile["version"].get(str(game_version), {})
            # workaround to save the correct dan grade by using the course mcode
            # because omnimix force unlocks all dan courses with <grade __type="u8">1</grade> in coursedb.xml
            if is_omni:
                n = note[0]
                mcode = int(n.find("mcode").text)
                if int(n.find("clearkind").text) != 1:
                    for grade, course_id in enumerate(range(1000, 1011), start=1):
                        if playstyle in (0, 2) and mcode in (course_id, course_id + 11):
                            single_grade = grade
                        elif playstyle == 1 and mcode in (
                            course_id + 1000,
                            course_id + 1000 + 11,
                        ):
                            double_grade = grade

            game_profile["single_grade"] = max(
                single_grade, game_profile.get("single_grade", single_grade)
            )
            game_profile["double_grade"] = max(
                double_grade, game_profile.get("double_grade", double_grade)
            )

            profile["version"][str(game_version)] = game_profile
            db.table("ddr_profile").upsert(profile, where("card") == refid)

        response = E.response(
            E.playerdata(
                E.result(0, __type="s32"),
            )
        )

    elif mode == "rivalload":
        loadflag = int(data.find("loadflag").text)
        ddrcode = int(data.find("ddrcode").text)
        pcbid = data.find("pcbid").text
        shoparea = data.find("shoparea").text

        if loadflag == 1:
            all_scores = {}
            for record in db.table("ddr_scores").search(
                (where("game_version") == game_version)
                & (where("pcbid") == pcbid)
                & (where("ddr_id") != 0)
            ):
                ddr_id = record["ddr_id"]
                mcode = record["mcode"]
                difficulty = record["difficulty"]
                score = record["score"]

                if (mcode, difficulty) not in all_scores or score > all_scores[
                    (mcode, difficulty)
                ].get("score"):
                    all_scores[mcode, difficulty] = {
                        "game_version": game_version,
                        "ddr_id": ddr_id,
                        "mcode": mcode,
                        "difficulty": difficulty,
                        "rank": record["rank"],
                        "lamp": record["lamp"],
                        "score": score,
                        "exscore": record["exscore"],
                        "ghostid": record.doc_id,
                    }
            scores = list(all_scores.values())

        elif loadflag == 2:
            all_scores = {}
            for record in db.table("ddr_scores").search(
                (where("game_version") == game_version)
                & (where("shoparea") == shoparea)
                & (where("ddr_id") != 0)
            ):
                ddr_id = record["ddr_id"]
                mcode = record["mcode"]
                difficulty = record["difficulty"]
                score = record["score"]

                if (mcode, difficulty) not in all_scores or score > all_scores[
                    (mcode, difficulty)
                ].get("score"):
                    all_scores[mcode, difficulty] = {
                        "game_version": game_version,
                        "ddr_id": ddr_id,
                        "mcode": mcode,
                        "difficulty": difficulty,
                        "rank": record["rank"],
                        "lamp": record["lamp"],
                        "score": score,
                        "exscore": record["exscore"],
                        "ghostid": record.doc_id,
                    }
            scores = list(all_scores.values())

        elif loadflag == 4:
            all_scores = {}
            for record in db.table("ddr_scores").search(
                (where("game_version") == game_version) & (where("ddr_id") != 0)
            ):
                ddr_id = record["ddr_id"]
                mcode = record["mcode"]
                difficulty = record["difficulty"]
                score = record["score"]

                if (mcode, difficulty) not in all_scores or score > all_scores[
                    (mcode, difficulty)
                ].get("score"):
                    all_scores[mcode, difficulty] = {
                        "game_version": game_version,
                        "ddr_id": ddr_id,
                        "mcode": mcode,
                        "difficulty": difficulty,
                        "rank": record["rank"],
                        "lamp": record["lamp"],
                        "score": score,
                        "exscore": record["exscore"],
                        "ghostid": record.doc_id,
                    }
            scores = list(all_scores.values())

        elif loadflag in (8, 16, 32):
            scores = []
            for s in db.table("ddr_scores_best").search(where("ddr_id") == ddrcode):
                scores.append(s)

        load = []
        names = {}

        profiles = get_db().table("ddr_profile")
        for p in profiles:
            names[p["ddr_id"]] = {}
            try:
                names[p["ddr_id"]]["name"] = p["version"][str(game_version)][
                    "common"
                ].split(",")[27]
                names[p["ddr_id"]]["area"] = int(
                    str(p["version"][str(game_version)]["common"].split(",")[3]), 16
                )
            except KeyError:
                names[p["ddr_id"]]["name"] = "UNKNOWN"
                names[p["ddr_id"]]["area"] = 13

        response = E.response(
            E.playerdata(
                E.result(0, __type="s32"),
                E.data(
                    E.recordtype(loadflag, __type="s32"),
                    *[
                        E.record(
                            E.mcode(r["mcode"], __type="u32"),
                            E.notetype(r["difficulty"], __type="u8"),
                            E.rank(r["rank"], __type="u8"),
                            E.clearkind(r["lamp"], __type="u8"),
                            E.flagdata(0, __type="u8"),
                            E.name(
                                names[r["ddr_id"]]["name"]
                                if r["ddr_id"] in names
                                else "UNKNOWN",
                                __type="str",
                            ),
                            E.area(
                                names[r["ddr_id"]]["area"]
                                if r["ddr_id"] in names
                                else 13,
                                __type="s32",
                            ),
                            E.code(r["ddr_id"], __type="s32"),
                            E.score(r["score"], __type="s32"),
                            E.ghostid(r["ghostid"], __type="s32"),
                        )
                        for r in scores
                    ],
                ),
            )
        )

    elif mode == "inheritance":
        response = E.response(
            E.playerdata(
                E.result(0, __type="s32"),
                E.InheritanceStatus(1, __type="s32"),
            )
        )

    else:
        response = E.response(
            E.playerdata(
                E.result(1, __type="s32"),
            )
        )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/playerdata/usergamedata_recv")
async def playerdata_usergamedata_recv(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    data = request_info["root"][0].find("data")
    cid = data.find("refid").text
    profile = get_game_profile(cid, game_version)

    db = get_db().table("ddr_profile")
    all_profiles_for_card = db.get(Query().card == cid)

    if all_profiles_for_card is None:
        load = [
            b64encode(
                str.encode(
                    "1,d,1111111,1,0,0,0,0,0,ffffffffffffffff,0,0,0,0,0,0,0,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,,1010-1010,,,,,,"
                ).decode()
            ),
            b64encode(
                str.encode(
                    "0,3,0,0,0,0,0,3,0,0,0,0,1,2,0,0,0,10.000000,10.000000,10.000000,10.000000,0.000000,0.000000,0.000000,0.000000,,,,,,,,"
                ).decode()
            ),
            b64encode(
                str.encode(
                    "1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,,,,,,,,"
                ).decode()
            ),
            b64encode(
                str.encode(
                    "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,,,,,,,,"
                ).decode()
            ),
        ]
    else:
        calories_disp = ["Off", "On"]
        character = [
            "All Character Random",
            "Man Random",
            "Female Random",
            "Yuni",
            "Rage",
            "Afro",
            "Jenny",
            "Emi",
            "Baby-Lon",
            "Gus",
            "Ruby",
            "Alice",
            "Julio",
            "Bonnie",
            "Zero",
            "Rinon",
        ]
        arrow_skin = ["Normal", "X", "Classic", "Cyber", "Medium", "Small", "Dot"]
        screen_filter = ["Off", "Dark", "Darker", "Darkest"]
        guideline = ["Off", "Border", "Center"]
        priority = ["Judgment", "Arrow"]
        timing_disp = ["Off", "On"]

        common = profile["common"].split(",")
        common[5] = calories_disp.index(profile["calories_disp"])
        common[6] = character.index(profile["character"])
        common[9] = 1  # Mobile link
        common_load = ",".join([str(i) for i in common])

        option = profile["option"].split(",")
        option[13] = arrow_skin.index(profile["arrow_skin"])
        option[14] = screen_filter.index(profile["filter"])
        option[15] = guideline.index(profile["guideline"])
        option[17] = priority.index(profile["priority"])
        option[18] = timing_disp.index(profile["timing_disp"])
        option_load = ",".join([str(i) for i in option])

        rival = profile["rival"].split(",")
        rival_ids = [
            profile.get("rival_1_ddr_id", 0),
            profile.get("rival_2_ddr_id", 0),
            profile.get("rival_3_ddr_id", 0),
        ]
        for idx, r in enumerate(rival_ids, start=3):
            if r != 0:
                rival[idx] = idx - 2
                rival[idx + 8] = get_common(r, game_version, 4)
        rival_load = ",".join([str(i) for i in rival])

        load = [
            b64encode(str.encode(common_load.split("ffffffff,COMMON,")[1])).decode(),
            b64encode(str.encode(option_load.split("ffffffff,OPTION,")[1])).decode(),
            b64encode(str.encode(profile["last"].split("ffffffff,LAST,")[1])).decode(),
            b64encode(str.encode(rival_load.split("ffffffff,RIVAL,")[1])).decode(),
        ]

    response = E.response(
        E.playerdata(
            E.result(0, __type="s32"),
            E.player(
                E.record(
                    *[E.d(p, __type="str") for p in load],
                ),
                E.record_num(4, __type="u32"),
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/playerdata/usergamedata_send")
async def playerdata_usergamedata_send(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    data = request_info["root"][0].find("data")
    cid = data.find("refid").text
    num = int(data.find("datanum").text)

    profile = get_profile(cid)
    game_profile = profile["version"].get(str(game_version), {})

    if num == 1:
        game_profile["common"] = b64decode(
            data.find("record")[0].text.split("<bin1")[0]
        ).decode(encoding="utf-8", errors="ignore")

    elif num == 4:
        game_profile["common"] = b64decode(
            data.find("record")[0].text.split("<bin1")[0]
        ).decode(encoding="utf-8", errors="ignore")
        game_profile["option"] = b64decode(
            data.find("record")[1].text.split("<bin1")[0]
        ).decode(encoding="utf-8", errors="ignore")
        game_profile["last"] = b64decode(
            data.find("record")[2].text.split("<bin1")[0]
        ).decode(encoding="utf-8", errors="ignore")
        game_profile["rival"] = b64decode(
            data.find("record")[3].text.split("<bin1")[0]
        ).decode(encoding="utf-8", errors="ignore")
        for r in ("rival_1_ddr_id", "rival_2_ddr_id", "rival_3_ddr_id"):
            if r not in game_profile:
                game_profile[r] = 0

    profile["version"][str(game_version)] = game_profile

    get_db().table("ddr_profile").upsert(profile, where("card") == cid)

    response = E.response(
        E.playerdata(
            E.result(0, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
