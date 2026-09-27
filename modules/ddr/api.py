from typing import Optional, Dict, List, Tuple
from os import path
import json
import struct

import lxml.etree as ET
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route, Router
from tinydb import where

import utils.card as conv
from core_database import get_db
from modules.webapi import endpoint, read_model
from utils.lz77 import lz77_decode


class DDR_Profile_Main_Items(BaseModel):
    card: str
    pin: str


class DDR_Profile_19_Items(BaseModel):
    game_version: Optional[int]
    calories_disp: Optional[bool]
    character: Optional[str]
    arrow_skin: Optional[str]
    filter: Optional[str]
    guideline: Optional[str]
    priority: Optional[str]
    timing_disp: Optional[bool]
    common: Optional[str]
    option: Optional[str]
    last: Optional[str]
    rival: Optional[str]
    rival_1_ddr_id: Optional[int]
    rival_2_ddr_id: Optional[int]
    rival_3_ddr_id: Optional[int]
    single_grade: Optional[int]
    double_grade: Optional[int]


class DDR_Profile_20_Items(BaseModel):
    game_version: Optional[int]
    common_dancername: Optional[str]
    common_area: Optional[str]
    rival_1_ddr_id: Optional[int]
    rival_2_ddr_id: Optional[int]
    rival_3_ddr_id: Optional[int]
    customize: Optional[dict]


@endpoint
async def ddr_profiles(request: Request):
    return get_db().table("ddr_profile").all()


@endpoint
async def ddr_profile_id(request: Request):
    ddr_id = request.path_params["ddr_id"]
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    return get_db().table("ddr_profile").get(where("ddr_id") == ddr_id)


@endpoint
async def ddr_profile_id_patch(request: Request):
    ddr_id = request.path_params["ddr_id"]
    item = await read_model(request, DDR_Profile_Main_Items)
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    profile = get_db().table("ddr_profile").get(where("ddr_id") == ddr_id)

    profile["card"] = item.card
    profile["pin"] = item.pin

    get_db().table("ddr_profile").upsert(profile, where("ddr_id") == ddr_id)
    return Response(status_code=204)


@endpoint
async def ddr_profile_id_19_patch(request: Request):
    ddr_id = request.path_params["ddr_id"]
    item = await read_model(request, DDR_Profile_19_Items)
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    profile = get_db().table("ddr_profile").get(where("ddr_id") == ddr_id)
    game_profile = profile["version"].get("19", {})

    game_profile["game_version"] = item.game_version
    game_profile["calories_disp"] = "On" if item.calories_disp else "Off"
    game_profile["character"] = item.character
    game_profile["arrow_skin"] = item.arrow_skin
    game_profile["filter"] = item.filter
    game_profile["guideline"] = item.guideline
    game_profile["priority"] = item.priority
    game_profile["timing_disp"] = "On" if item.timing_disp else "Off"
    game_profile["common"] = item.common
    game_profile["option"] = item.option
    game_profile["last"] = item.last
    game_profile["rival"] = item.rival
    game_profile["rival_1_ddr_id"] = item.rival_1_ddr_id
    game_profile["rival_2_ddr_id"] = item.rival_2_ddr_id
    game_profile["rival_3_ddr_id"] = item.rival_3_ddr_id

    profile["version"]["19"] = game_profile
    get_db().table("ddr_profile").upsert(profile, where("ddr_id") == ddr_id)
    return Response(status_code=204)


@endpoint
async def ddr_profile_id_20_patch(request: Request):
    ddr_id = request.path_params["ddr_id"]
    item = await read_model(request, DDR_Profile_20_Items)
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    profile = get_db().table("ddr_profile").get(where("ddr_id") == ddr_id)
    game_profile = profile["version"].get("20", {})

    game_profile["game_version"] = item.game_version
    game_profile["common_dancername"] = item.common_dancername
    game_profile["common_area"] = item.common_area
    game_profile["rival_1_ddr_id"] = item.rival_1_ddr_id
    game_profile["rival_2_ddr_id"] = item.rival_2_ddr_id
    game_profile["rival_3_ddr_id"] = item.rival_3_ddr_id
    game_profile["customize"] = item.customize

    profile["version"]["20"] = game_profile
    get_db().table("ddr_profile").upsert(profile, where("ddr_id") == ddr_id)
    return Response(status_code=204)


@endpoint
async def ddr_card_to_profile(request: Request):
    card = request.path_params["card"]
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
    else:
        card = "".join([c for c in card if c in conv.valid_characters])
        uid = conv.to_uid(card)
    profile = get_db().table("ddr_profile").get(where("card") == uid)
    return profile


@endpoint
async def ddr_scores(request: Request):
    return get_db().table("ddr_scores").all()


@endpoint
async def ddr_scores_id(request: Request):
    ddr_id = request.path_params["ddr_id"]
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    return get_db().table("ddr_scores").search((where("ddr_id") == ddr_id))


@endpoint
async def ddr_scores_best(request: Request):
    return get_db().table("ddr_scores_best").all()


@endpoint
async def ddr_scores_best_id(request: Request):
    ddr_id = request.path_params["ddr_id"]
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    return get_db().table("ddr_scores_best").search((where("ddr_id") == ddr_id))


@endpoint
async def ddr_scores_mcode_all(request: Request):
    mcode = int(request.path_params["mcode"])
    return get_db().table("ddr_scores").search((where("mcode") == mcode))


@endpoint
async def ddr_scores_mcode_best(request: Request):
    mcode = int(request.path_params["mcode"])
    return get_db().table("ddr_scores_best").search((where("mcode") == mcode))


class ARC:
    # https://github.com/DragonMinded/bemaniutils/blob/trunk/bemani/format/arc.py
    """
    Class representing an `.arc` file. These are found in DDR Ace, and possibly
    other games that use ESS. Given a serires of bytes, this will allow you to
    query included filenames as well as read the contents of any file inside the
    archive.
    """

    def __init__(self, data: bytes) -> None:
        self.__files: Dict[str, Tuple[int, int, int]] = {}
        self.__data = data
        self.__parse_file(data)

    def __parse_file(self, data: bytes) -> None:
        # Check file header
        if data[0:4] != bytes([0x20, 0x11, 0x75, 0x19]):
            # raise Exception("Unknown file format!")
            return Response(status_code=406)

        # Grab header offsets
        (_, numfiles, _) = struct.unpack("<III", data[4:16])

        for fno in range(numfiles):
            start = 16 + (16 * fno)
            end = start + 16
            (nameoffset, fileoffset, uncompressedsize, compressedsize) = struct.unpack(
                "<IIII", data[start:end]
            )
            name = ""

            while data[nameoffset] != 0:
                name = name + data[nameoffset : (nameoffset + 1)].decode("ascii")
                nameoffset = nameoffset + 1

            self.__files[name] = (fileoffset, uncompressedsize, compressedsize)

    @property
    def filenames(self) -> List[str]:
        return [f for f in self.__files]

    def read_file(self, filename: str) -> bytes:
        (fileoffset, uncompressedsize, compressedsize) = self.__files[filename]

        if compressedsize == uncompressedsize:
            # Just stored
            return self.__data[fileoffset : (fileoffset + compressedsize)]
        else:
            # Compressed
            return lz77_decode(
                self.__data[fileoffset : (fileoffset + compressedsize)]
            )


@endpoint
async def ddr_receive_mdb(request: Request):
    form = await request.form()
    upload = form["file"]
    data = await upload.read()
    arc = ARC(data)
    try:
        mdb_new = ET.fromstring(
            arc.read_file("data/gamedata/musicdb.xml"),
            parser=ET.XMLParser(encoding="utf-8"),
        )
    except KeyError:
        return Response(status_code=406)

    def get_attr(attrname):
        try:
            mdb[mcode][attrname] = attr.find(attrname).text.rstrip()
        except AttributeError:
            mdb[mcode][attrname] = ""

    mdb = {}
    for attr in mdb_new:
        mcode = attr.find("mcode").text
        mdb[mcode] = {}

        attributes = (
            "basename",
            "title",
            "title_yomi",
            "artist",
            "bpmmin",
            "bpmmax",
            "series",
            "eventno",
            "bemaniflag",
            "bgstage",
            "movie",
            "genreflag",
            "voice",
        )

        for a in attributes:
            get_attr(a)

        mdb[mcode]["diffLv"] = attr.find("diffLv").text.split(" ")

    ddr_metadata = path.join("webui", "ddr.json")
    if path.exists(ddr_metadata):
        with open(ddr_metadata, "r", encoding="utf-8") as fp:
            mdb_old = json.load(fp)
            for mcode in mdb_old.keys():
                mdb[mcode] = mdb_old[mcode]

    with open(ddr_metadata, "w", encoding="utf-8") as fp:
        json.dump(mdb, fp, indent=4, ensure_ascii=False)

    return Response(status_code=201)


router = Router(
    routes=[
        Route("/profiles", ddr_profiles, methods=["GET"]),
        Route("/profiles/{ddr_id}", ddr_profile_id, methods=["GET"]),
        Route("/profiles/{ddr_id}", ddr_profile_id_patch, methods=["PATCH"]),
        Route("/profiles/{ddr_id}/19", ddr_profile_id_19_patch, methods=["PATCH"]),
        Route("/profiles/{ddr_id}/20", ddr_profile_id_20_patch, methods=["PATCH"]),
        Route("/card/{card}", ddr_card_to_profile, methods=["GET"]),
        Route("/scores", ddr_scores, methods=["GET"]),
        Route("/scores/{ddr_id}", ddr_scores_id, methods=["GET"]),
        Route("/scores_best", ddr_scores_best, methods=["GET"]),
        Route("/scores_best/{ddr_id}", ddr_scores_best_id, methods=["GET"]),
        Route("/mcode/{mcode}/all", ddr_scores_mcode_all, methods=["GET"]),
        Route("/mcode/{mcode}/best", ddr_scores_mcode_best, methods=["GET"]),
        Route("/parse_mdb/upload", ddr_receive_mdb, methods=["POST"]),
    ]
)
