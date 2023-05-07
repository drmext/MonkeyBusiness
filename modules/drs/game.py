import xml.etree.ElementTree as ET
from os import path

from tinydb import Query, where

import config
import random
import time

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["REC"]


def get_profile(cid):
    return get_db().table("dancerush_profile").get(where("card") == cid)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


def get_id_from_profile(cid):
    profile = get_db().table("dancerush_profile").get(where("card") == cid)

    djid = "%08d" % profile["drs_id"]
    djid_split = "-".join([djid[:4], djid[4:]])

    return profile["drs_id"], djid_split


@router.post("/{gameinfo}/game/get_common")
async def drs_game_get_common(request: Request):
    request_info = await core_process_request(request)

    songs = {}

    # TODO: server side song unlock is incomplete, use hex edits for now
    for f in (
        path.join("modules", "drs", "music-info-base.xml"),
        path.join("music-info-base.xml"),
    ):
        if path.exists(f):
            with open(f, "r", encoding="utf-8") as fp:
                tree = ET.parse(fp, ET.XMLParser())
                root = tree.getroot()

                for entry in root:
                    mid = entry.get("id")
                    songs[mid] = {}
                    for atr in (
                        "title_name",
                        "title_yomigana",
                        "artist_name",
                        "artist_yomigana",
                        "bpm_max",
                        "bpm_min",
                        # "distribution_date",
                        "volume",
                        "bg_no",
                        "region",
                        # "limitation_type",
                        # "price",
                        "genre",
                        "play_video_flags",
                        "is_fixed",
                        "version",
                        "demo_pri",
                        "license",
                        "color1",
                        "color2",
                        "color3",
                    ):
                        songs[mid][atr] = entry.find(f"info/{atr}").text
                        if songs[mid][atr] == None:
                            songs[mid][atr] = ""
                    for atr in (
                        "1b",
                        "1a",
                        "2b",
                        "2a",
                    ):
                        songs[mid][f"{atr}_difnum"] = entry.find(
                            f"difficulty/fumen_{atr}/difnum"
                        ).text
                        # songs[mid][f"{atr}_playable"] = entry.find(f"difficulty/fumen_{atr}/playable").text
            break

    response = E.response(
        E.game(
            E.mdb(
                *[
                    E.music(
                        E.info(
                            E.title_name(songs[s]["title_name"], __type="str"),
                            E.title_yomigana(songs[s]["title_yomigana"], __type="str"),
                            E.artist_name(songs[s]["artist_name"], __type="str"),
                            E.artist_yomigana(
                                songs[s]["artist_yomigana"], __type="str"
                            ),
                            E.bpm_max(songs[s]["bpm_max"], __type="u32"),
                            E.bpm_min(songs[s]["bpm_min"], __type="u32"),
                            E.distribution_date(20180427, __type="u32"),
                            E.volume(songs[s]["volume"], __type="u16"),
                            E.bg_no(songs[s]["bg_no"], __type="u16"),
                            E.region("JUAKYC", __type="str"),
                            E.limitation_type(3, __type="u8"),
                            E.price(0, __type="s32"),
                            E.genre(songs[s]["genre"], __type="u32"),
                            E.play_video_flags(
                                songs[s]["play_video_flags"], __type="u32"
                            ),
                            E.is_fixed(songs[s]["is_fixed"], __type="u8"),
                            E.version(songs[s]["version"], __type="u8"),
                            E.demo_pri(songs[s]["demo_pri"], __type="u8"),
                            E.license(songs[s]["license"], __type="str"),
                            E.color1(int(songs[s]["color1"], 16), __type="u32"),
                            E.color2(int(songs[s]["color2"], 16), __type="u32"),
                            E.color3(int(songs[s]["color3"], 16), __type="u32"),
                        ),
                        E.difficulty(
                            E.fumen_1b(
                                E.difnum(songs[s]["1b_difnum"], __type="u8"),
                                E.playable(1, __type="u8"),
                            ),
                            E.fumen_1a(
                                E.difnum(songs[s]["1a_difnum"], __type="u8"),
                                E.playable(1, __type="u8"),
                            ),
                            E.fumen_2b(
                                E.difnum(songs[s]["2b_difnum"], __type="u8"),
                                E.playable(1, __type="u8"),
                            ),
                            E.fumen_2a(
                                E.difnum(songs[s]["2a_difnum"], __type="u8"),
                                E.playable(1, __type="u8"),
                            ),
                        ),
                        id=s,
                    )
                    for s in songs
                ],
            ),
            E.extra(*[E.info(E.music_id(i, __type="s32")) for i in songs]),
            E.contest(
                *[
                    E.info(
                        E.contest_id(i, __type="s32"),
                        E.start_date(1683422123358, __type="u64"),
                        E.end_date(1693422123358, __type="u64"),
                        E.title("", __type="str"),
                        E.regulation(i, __type="s32"),
                        E.target_music(
                            E.music(
                                E.music_id(1, __type="s32"),
                                E.music_type("1b", __type="str"),
                            )
                        ),
                    )
                    for i in range(1, 3)
                ]
            ),
            E.event(
                *[
                    E.info(
                        E.event_id(e, __type="s32"),
                        E.start_date(1683422123358, __type="u64"),
                        E.end_date(1693422123358, __type="u64"),
                        E.param("", __type="str"),
                    )
                    for e in range(1, 14)
                ]
            ),
            # E.kac2020(
            #     E.reward(
            #         E.data(
            #             E.music_id(1, __type="s32"),
            #             E.is_available(1, __type="bool"),
            #         )
            #     )
            # ),
            # E.silhouette(E.info(E.silhouette_id(i, __type="s32"))),
            # E.music_condition(*[E.music(E.conditions(), id=s) for s in songs]),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/get_playdata_{player}")
async def drs_game_get_playdata(player: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    dataid = request_info["root"][0].find("userid/refid").text
    profile = get_game_profile(dataid, game_version)

    if profile:
        djid, djid_split = get_id_from_profile(dataid)

        response = E.response(
            E.game(
                E.result(0, __type="s32"),
                E.userid(E.code(djid, __type="s32")),
                E.profile(E.name(profile["name"], __type="str")),
                E.playinfo(
                    E.softcode("", __type="str"),
                    E.start_date(1683422123358, __type="u64"),
                    E.end_date(1683422123358, __type="u64"),
                    E.mode_id(profile["mode_id"], __type="s32"),
                    E.music_id(profile["music_id"], __type="s32"),
                    E.music_type(profile["music_type"], __type="str"),
                    E.pcbid("0", __type="str"),
                    E.locid("EA000001", __type="str"),
                ),
                E.paramdata(
                    *[
                        E.data(
                            E.data_type(p[0], __type="s32"),
                            E.data_id(p[1], __type="s32"),
                            E.param_list(p[2], __type="s32"),
                        )
                        for p in profile["params"]
                    ]
                ),
                E.dance_dance_rush(E.data()),
                E.summer_dance_damp(E.data()),
                E.kac2020(),
                E.hidden_param(0, __type="s32"),
                E.play_count(1001, __type="u32"),
                E.daily_count(301, __type="u32"),
                E.play_chain(31, __type="u32"),
            )
        )

    else:
        response = E.response(
            E.game(
                E.result(1, __type="s32"),
            )
        )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/lock_multi_login_{player}")
async def drs_game_lock_multi_login(player: str, request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.game())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/sign_up_{player}")
async def drs_game_sign_up(player: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0]

    dataid = root.find("userid/dataid").text
    cardno = root.find("userid/cardno").text
    name = root.find("profile/name").text

    db = get_db().table("dancerush_profile")
    all_profiles_for_card = db.get(Query().card == dataid)

    if all_profiles_for_card is None:
        all_profiles_for_card = {"card": dataid, "version": {}}

    if "drs_id" not in all_profiles_for_card:
        drs_id = random.randint(10000000, 99999999)
        all_profiles_for_card["drs_id"] = drs_id

    all_profiles_for_card["version"][str(game_version)] = {
        "game_version": game_version,
        "name": name,
        "mode_id": 0,
        "music_id": 1,
        "music_type": "1a",
        "params": [],
    }

    db.upsert(all_profiles_for_card, where("card") == dataid)

    response = E.response(E.game())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/get_musicscore_{player}")
async def drs_get_musicscore(player: str, request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    scores = []
    db = get_db()
    for record in db.table("drs_scores_best").search(
        (where("game_version") == game_version)
    ):
        scores.append(
            [
                record["music_id"],
                record["music_type"],
                record["score"],
                record["rank"],
                record["combo"],
                record["param"],
            ]
        )

    response = E.response(
        E.game(
            E.scoredata(
                *[
                    E.music(
                        E.music_id(s[0], __type="s32"),
                        E.music_type(s[1], __type="str"),
                        E.play_cnt(1, __type="s32"),
                        E.score(s[2], __type="s32"),
                        E.rank(s[3], __type="s32"),
                        E.combo(s[4], __type="s32"),
                        E.param(s[5], __type="s32"),
                        E.bestscore_date(1683422123358, __type="u64"),
                        E.lastplay_date(1683422123358, __type="u64"),
                    )
                    for s in scores
                ],
            ),
        ),
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/save_musicscore")
async def drs_save_musicscore(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    timestamp = time.time()

    root = request_info["root"][0][0]

    dataid = root.find("userid/refid").text
    profile = get_game_profile(dataid, game_version)
    djid, djid_split = get_id_from_profile(dataid)

    music_id = int(root.find("music_id").text)
    music_type = root.find("music_type").text
    mode = int(root.find("mode").text)
    score = int(root.find("score").text)
    rank = int(root.find("rank").text)
    combo = int(root.find("combo").text)
    param = int(root.find("param").text)
    perfect = int(root.find("member/perfect").text)
    great = int(root.find("member/great").text)
    good = int(root.find("member/good").text)
    bad = int(root.find("member/bad").text)

    db = get_db()
    db.table("drs_scores").insert(
        {
            "timestamp": timestamp,
            "game_version": game_version,
            "drs_id": djid,
            "music_id": music_id,
            "music_type": music_type,
            "mode": mode,
            "score": score,
            "rank": rank,
            "combo": combo,
            "param": param,
            "perfect": perfect,
            "great": great,
            "good": good,
            "bad": bad,
        },
    )

    best = db.table("drs_scores_best").get(
        (where("drs_id") == djid)
        & (where("game_version") == game_version)
        & (where("music_id") == music_id)
        & (where("music_type") == music_type)
    )
    best = {} if best is None else best

    best_score_data = {
        "game_version": game_version,
        "drs_id": djid,
        "name": profile["name"],
        "music_id": music_id,
        "music_type": music_type,
        "score": max(score, best.get("score", score)),
        "rank": max(rank, best.get("rank", rank)),
        "combo": max(combo, best.get("combo", combo)),
        "param": param,
    }

    db.table("drs_scores_best").upsert(
        best_score_data,
        (where("drs_id") == djid)
        & (where("game_version") == game_version)
        & (where("music_id") == music_id)
        & (where("music_type") == music_type),
    )

    response = E.response(E.game())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/game/save_playdata")
async def drs_save_musicscore(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0][0]

    dataid = root.find("userid/refid").text

    profile = get_profile(dataid)
    game_profile = profile["version"].get(str(game_version), {})

    game_profile["mode_id"] = int(root.find("playinfo/mode_id").text)
    game_profile["music_id"] = int(root.find("playinfo/music_id").text)
    game_profile["music_type"] = root.find("playinfo/music_type").text

    old_params = game_profile["params"]
    params = {}

    for old in old_params:
        t = str(old[0])
        i = str(old[1])
        p = old[2]
        if t not in params:
            params[t] = {}
            if i not in params[t]:
                params[t][i] = {}
        params[t][i] = p

    for info in root.find("paramdata"):
        t = info.find("data_type").text
        i = info.find("data_id").text
        p = info.find("param_list")

        if t not in params:
            params[t] = {}
            if i not in params[t]:
                params[t][i] = {}
        params[t][i] = [int(x) for x in p.text.split(" ")]

    params_list = []

    for t in params:
        for i in params[t]:
            params_list.append([int(t), int(i), params[t][i]])

    game_profile["params"] = params_list

    profile["version"][str(game_version)] = game_profile

    get_db().table("dancerush_profile").upsert(profile, where("card") == dataid)

    response = E.response(E.game())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
