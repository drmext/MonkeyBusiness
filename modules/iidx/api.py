from fastapi import APIRouter, Request, Response, File, UploadFile

from core_common import core_process_request, core_prepare_response, E

from tinydb import Query, where
from core_database import get_db
from pydantic import BaseModel
from typing import Optional

import config
import utils.card as conv
import utils.musicdata_tool as mdt
from utils.lz77 import EamuseLZ77

import xml.etree.ElementTree as ET
import ujson as json
from os import path


router = APIRouter(prefix="/iidx", tags=["api_iidx"])


class IIDX_Profile_Main_Items(BaseModel):
    card: str
    pin: str


class IIDX_Profile_Version_Items(BaseModel):
    djname: Optional[str]
    region: Optional[int]
    head: Optional[int]
    hair: Optional[int]
    face: Optional[int]
    hand: Optional[int]
    body: Optional[int]
    frame: Optional[int]
    turntable: Optional[int]
    explosion: Optional[int]
    bgm: Optional[int]
    sudden: Optional[int]
    categoryvoice: Optional[int]
    note: Optional[int]
    fullcombo: Optional[int]
    keybeam: Optional[int]
    judgestring: Optional[int]
    soundpreview: Optional[int]
    grapharea: Optional[int]
    effector_lock: Optional[int]
    effector_type: Optional[int]
    explosion_size: Optional[int]
    alternate_hcn: Optional[int]
    kokokara_start: Optional[int]
    show_category_grade: Optional[int]
    show_category_status: Optional[int]
    show_category_difficulty: Optional[int]
    show_category_alphabet: Optional[int]
    show_category_rival_play: Optional[int]
    show_category_rival_winlose: Optional[int]
    show_category_all_rival_play: Optional[int]
    show_category_arena_winlose: Optional[int]
    show_rival_shop_info: Optional[int]
    hide_play_count: Optional[int]
    show_score_graph_cutin: Optional[int]
    hide_iidx_id: Optional[int]
    classic_hispeed: Optional[int]
    beginner_option_swap: Optional[int]
    show_lamps_as_no_play_in_arena: Optional[int]
    skin_customize_flag_frame: Optional[int]
    skin_customize_flag_bgm: Optional[int]
    skin_customize_flag_lane: Optional[int]
    sp_rival_1_iidx_id: Optional[int]
    sp_rival_2_iidx_id: Optional[int]
    sp_rival_3_iidx_id: Optional[int]
    sp_rival_4_iidx_id: Optional[int]
    sp_rival_5_iidx_id: Optional[int]
    sp_rival_6_iidx_id: Optional[int]
    dp_rival_1_iidx_id: Optional[int]
    dp_rival_2_iidx_id: Optional[int]
    dp_rival_3_iidx_id: Optional[int]
    dp_rival_4_iidx_id: Optional[int]
    dp_rival_5_iidx_id: Optional[int]
    dp_rival_6_iidx_id: Optional[int]


@router.get("/profiles")
async def iidx_profiles():
    return get_db().table("iidx_profile").all()


@router.get("/profiles/{iidx_id}")
async def iidx_profile_id(iidx_id: str):
    iidx_id = int("".join([i for i in iidx_id if i.isnumeric()]))
    return get_db().table("iidx_profile").get(where("iidx_id") == iidx_id)


@router.patch("/profiles/{iidx_id}")
async def iidx_profile_id_patch(iidx_id: str, item: IIDX_Profile_Main_Items):
    iidx_id = int("".join([i for i in iidx_id if i.isnumeric()]))
    profile = get_db().table("iidx_profile").get(where("iidx_id") == iidx_id)

    profile["card"] = item.card
    profile["pin"] = item.pin

    get_db().table("iidx_profile").upsert(profile, where("iidx_id") == iidx_id)
    return Response(status_code=204)


@router.patch("/profiles/{iidx_id}/{version}")
async def iidx_profile_id_version_patch(
    iidx_id: str, version: int, item: IIDX_Profile_Version_Items
):
    if version != 30:
        # TODO: differentiate 18, 19, 20, 29, 30
        return Response(status_code=406)
    iidx_id = int("".join([i for i in iidx_id if i.isnumeric()]))
    profile = get_db().table("iidx_profile").get(where("iidx_id") == iidx_id)
    game_profile = profile["version"].get(str(version), {})

    game_profile["djname"] = item.djname
    game_profile["region"] = item.region
    game_profile["head"] = item.head
    game_profile["hair"] = item.hair
    game_profile["face"] = item.face
    game_profile["hand"] = item.hand
    game_profile["body"] = item.body
    game_profile["frame"] = item.frame
    game_profile["turntable"] = item.turntable
    game_profile["explosion"] = item.explosion
    game_profile["bgm"] = item.bgm
    game_profile["sudden"] = item.sudden
    game_profile["categoryvoice"] = item.categoryvoice
    game_profile["note"] = item.note
    game_profile["fullcombo"] = item.fullcombo
    game_profile["keybeam"] = item.keybeam
    game_profile["judgestring"] = item.judgestring
    game_profile["soundpreview"] = item.soundpreview
    game_profile["grapharea"] = item.grapharea
    game_profile["effector_lock"] = item.effector_lock
    game_profile["effector_type"] = item.effector_type
    game_profile["explosion_size"] = item.explosion_size
    game_profile["alternate_hcn"] = item.alternate_hcn
    game_profile["kokokara_start"] = item.kokokara_start
    game_profile["_show_category_grade"] = item.show_category_grade
    game_profile["_show_category_status"] = item.show_category_status
    game_profile["_show_category_difficulty"] = item.show_category_difficulty
    game_profile["_show_category_alphabet"] = item.show_category_alphabet
    game_profile["_show_category_rival_play"] = item.show_category_rival_play
    game_profile["_show_category_rival_winlose"] = item.show_category_rival_winlose
    game_profile["_show_category_all_rival_play"] = item.show_category_all_rival_play
    game_profile["_show_category_arena_winlose"] = item.show_category_arena_winlose
    game_profile["_show_rival_shop_info"] = item.show_rival_shop_info
    game_profile["_hide_play_count"] = item.hide_play_count
    game_profile["_show_score_graph_cutin"] = item.show_score_graph_cutin
    game_profile["_hide_iidx_id"] = item.hide_iidx_id
    game_profile["_classic_hispeed"] = item.classic_hispeed
    game_profile["_beginner_option_swap"] = item.beginner_option_swap
    game_profile[
        "_show_lamps_as_no_play_in_arena"
    ] = item.show_lamps_as_no_play_in_arena
    game_profile["skin_customize_flag_frame"] = item.skin_customize_flag_frame
    game_profile["skin_customize_flag_bgm"] = item.skin_customize_flag_bgm
    game_profile["skin_customize_flag_lane"] = item.skin_customize_flag_lane
    game_profile["sp_rival_1_iidx_id"] = item.sp_rival_1_iidx_id
    game_profile["sp_rival_2_iidx_id"] = item.sp_rival_2_iidx_id
    game_profile["sp_rival_3_iidx_id"] = item.sp_rival_3_iidx_id
    game_profile["sp_rival_4_iidx_id"] = item.sp_rival_4_iidx_id
    game_profile["sp_rival_5_iidx_id"] = item.sp_rival_5_iidx_id
    game_profile["sp_rival_6_iidx_id"] = item.sp_rival_6_iidx_id
    game_profile["dp_rival_1_iidx_id"] = item.dp_rival_1_iidx_id
    game_profile["dp_rival_2_iidx_id"] = item.dp_rival_2_iidx_id
    game_profile["dp_rival_3_iidx_id"] = item.dp_rival_3_iidx_id
    game_profile["dp_rival_4_iidx_id"] = item.dp_rival_4_iidx_id
    game_profile["dp_rival_5_iidx_id"] = item.dp_rival_5_iidx_id
    game_profile["dp_rival_6_iidx_id"] = item.dp_rival_6_iidx_id

    profile["version"][str(version)] = game_profile
    get_db().table("iidx_profile").upsert(profile, where("iidx_id") == iidx_id)
    return Response(status_code=204)


@router.get("/card/{card}")
async def iidx_card_to_profile(card: str):
    card = card.upper()
    lookalike = {
        "I": "1",
        "O": "0",
        "Q": "0",
        "V": "U",
    }
    for k, v in lookalike.items():
        card = card.replace(k, v)
    if card.startswith("E004") or card.startswith("012E"):
        card = "".join([c for c in card if c in "0123456789ABCDEF"])
        uid = card
        kid = conv.to_konami_id(card)
    else:
        card = "".join([c for c in card if c in conv.valid_characters])
        uid = conv.to_uid(card)
        kid = card
    profile = get_db().table("iidx_profile").get(where("card") == uid)
    return profile


@router.get("/scores")
async def iidx_scores():
    return get_db().table("iidx_scores").all()


@router.get("/scores/{iidx_id}")
async def iidx_scores_id(iidx_id: str):
    iidx_id = int("".join([i for i in iidx_id if i.isnumeric()]))
    return get_db().table("iidx_scores").search((where("iidx_id") == iidx_id))


@router.get("/scores_best")
async def iidx_scores_best():
    return get_db().table("iidx_scores_best").all()


@router.get("/scores_best/{iidx_id}")
async def iidx_scores_best_id(iidx_id: str):
    iidx_id = int("".join([i for i in iidx_id if i.isnumeric()]))
    return get_db().table("iidx_scores_best").search((where("iidx_id") == iidx_id))


@router.get("/music_id/{music_id}/all")
async def iidx_scores_id(music_id: int):
    return get_db().table("iidx_scores").search((where("music_id") == music_id))


@router.get("/music_id/{music_id}/best")
async def iidx_scores_id_best(music_id: int):
    return get_db().table("iidx_scores_best").search((where("music_id") == music_id))


@router.get("/class_best/{iidx_id}")
async def iidx_class_best(iidx_id: str):
    iidx_id = int("".join([i for i in iidx_id if i.isnumeric()]))
    return get_db().table("iidx_class_best").search((where("iidx_id") == iidx_id))


@router.get("/score_stats/all")
async def iidx_score_stats():
    return get_db().table("iidx_score_stats").all()


@router.get("/score_stats/{music_id}")
async def iidx_score_stats_song(music_id: int):
    return get_db().table("iidx_score_stats").search((where("music_id") == music_id))


@router.post("/parse_mdb/upload")
async def iidx_receive_mdb(file: UploadFile = File(...)) -> bytes:
    data = await file.read()

    iidx_bin = path.join("webui", "music_data.bin")
    iidx_vid = path.join("webui", "video_music_list.xml")
    iidx_metadata = path.join("webui", "iidx.json")

    if data[0:4] == b"IIDX":
        # data_ver = int.from_bytes(data[4:8], "little")
        with open(iidx_bin, "wb") as output:
            output.write(data)
        try:
            mdt.extract_file(iidx_bin, iidx_metadata)
            return Response(status_code=201)
        except Exception as e:
            print(e)
            return Response(status_code=422)
    else:
        # video_music_list.xml to fix broken characters in title/artist
        # (this should be a seperate route)
        try:
            with open(iidx_metadata, "r", encoding="utf-8") as f:
                music_data = json.load(f)

            with open(iidx_vid, "wb") as output:
                output.write(data)

            with open(iidx_vid, "r", encoding="utf-8") as fp:
                tree = ET.parse(fp, ET.XMLParser())
                root = tree.getroot()

                proper_names = {}
                for entry in root:
                    mid = int(entry.get("id"))
                    proper_names[mid] = {}
                    proper_names[mid]["title"] = entry.find("info/title_name").text
                    proper_names[mid]["artist"] = entry.find("info/artist_name").text

            for m in music_data["data"]:
                try:
                    mid = m["song_id"]
                    vid_title = proper_names[mid]["title"]
                    bin_title = m["title"]
                    if vid_title != bin_title:
                        m["title"] = vid_title
                        # print(vid_title, bin_title)
                    vid_artist = proper_names[mid]["artist"]
                    bin_artist = m["artist"]
                    if vid_artist != bin_artist:
                        m["artist"] = vid_artist
                        # print(vid_artist, bin_artist)
                except KeyError:
                    continue

            json.dump(
                music_data,
                open(iidx_metadata, "w", encoding="utf8"),
                indent=4,
                ensure_ascii=False,
                escape_forward_slashes=False,
            )
            return Response(status_code=201)
        except Exception as e:
            print(e)
            return Response(status_code=422)

    return Response(status_code=406)
