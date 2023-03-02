from fastapi import APIRouter, Request, Response, File, UploadFile

from core_common import core_process_request, core_prepare_response, E

from tinydb import Query, where
from core_database import get_db
from pydantic import BaseModel

import config
import utils.card as conv
from utils.lz77 import EamuseLZ77

import lxml.etree as ET
import ujson as json
import struct
from typing import Dict, List, Tuple
from os import path


router = APIRouter(prefix="/ddr", tags=["api_ddr"])


class DDR_Profile_Main_Items(BaseModel):
    card: str
    pin: str


class DDR_Profile_Version_Items(BaseModel):
    game_version: int
    calories_disp: bool
    character: str
    arrow_skin: str
    filter: str
    guideline: str
    priority: str
    timing_disp: bool
    common: str
    option: str
    last: str
    rival: str
    rival_1_ddr_id: int
    rival_2_ddr_id: int
    rival_3_ddr_id: int
    single_grade: int
    double_grade: int


@router.get("/profiles")
async def ddr_profiles():
    return get_db().table("ddr_profile").all()


@router.get("/profiles/{ddr_id}")
async def ddr_profile_id(ddr_id: str):
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    return get_db().table("ddr_profile").get(where("ddr_id") == ddr_id)


@router.patch("/profiles/{ddr_id}")
async def ddr_profile_id_patch(ddr_id: str, item: DDR_Profile_Main_Items):
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    profile = get_db().table("ddr_profile").get(where("ddr_id") == ddr_id)

    profile["card"] = item.card
    profile["pin"] = item.pin

    get_db().table("ddr_profile").upsert(profile, where("ddr_id") == ddr_id)
    return Response(status_code=204)


@router.patch("/profiles/{ddr_id}/{version}")
async def ddr_profile_id_version_patch(
    ddr_id: str, version: int, item: DDR_Profile_Version_Items
):
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    profile = get_db().table("ddr_profile").get(where("ddr_id") == ddr_id)
    game_profile = profile["version"].get(str(version), {})

    if version >= 19:
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

    profile["version"][str(version)] = game_profile
    get_db().table("ddr_profile").upsert(profile, where("ddr_id") == ddr_id)
    return Response(status_code=204)


@router.get("/card/{card}")
async def ddr_card_to_profile(card: str):
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
    profile = get_db().table("ddr_profile").get(where("card") == uid)
    return profile


@router.get("/scores")
async def ddr_scores():
    return get_db().table("ddr_scores").all()


@router.get("/scores/{ddr_id}")
async def ddr_scores_id(ddr_id: str):
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    return get_db().table("ddr_scores").search((where("ddr_id") == ddr_id))


@router.get("/scores_best")
async def ddr_scores_best():
    return get_db().table("ddr_scores_best").all()


@router.get("/scores_best/{ddr_id}")
async def ddr_scores_best_id(ddr_id: str):
    ddr_id = int("".join([i for i in ddr_id if i.isnumeric()]))
    return get_db().table("ddr_scores_best").search((where("ddr_id") == ddr_id))


@router.get("/mcode/{mcode}/all")
async def ddr_scores_id(mcode: int):
    return get_db().table("ddr_scores").search((where("mcode") == mcode))


@router.get("/mcode/{mcode}/best")
async def ddr_scores_id_best(mcode: int):
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
            return EamuseLZ77.decode(
                self.__data[fileoffset : (fileoffset + compressedsize)]
            )


@router.post("/parse_mdb/upload")
async def ddr_receive_mdb(file: UploadFile = File(...)) -> bytes:
    data = await file.read()
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
        json.dump(mdb, fp, indent=4, ensure_ascii=False, escape_forward_slashes=False)

    return Response(status_code=201)
