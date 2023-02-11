import xml.etree.ElementTree as ET
from os import path

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["PAN"]


@router.post("/{gameinfo}/op3_common/get_common_info")
async def op3_common_get_common_info(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.get_common_info(E.olupdate(E.delete_flag(0, __type="bool")))
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/op3_common/get_music_info")
async def op3_common_get_music_info(request: Request):
    request_info = await core_process_request(request)

    songs = {}

    revision = "21261"
    release_code = "2021090800"

    for f in (
        path.join("modules", "nostalgia", "music_list.xml"),
        path.join("music_list.xml"),
    ):
        if path.exists(f):
            with open(f, "r", encoding="shift_jisx0213") as fp:

                tree = ET.parse(fp, ET.XMLParser())
                root = tree.getroot()

                revision = root.get("revision")
                release_code = root.get("release_code")

                for entry in root:
                    mid = entry.get("index")
                    songs[mid] = {}
                    for atr in (
                        "priority",
                        "category_flag",
                        "primary_category",
                        "level_normal",
                        "level_hard",
                        "level_extreme",
                        "level_real",
                        "demo_popular",
                        "demo_bemani",
                        "destination_j",
                        "destination_a",
                        "destination_y",
                        "destination_k",
                        "offline",
                        "unlock_type",
                        "volume_bgm",
                        "volume_key",
                        "jk_jpn",
                        "jk_asia",
                        "jk_kor",
                        "jk_idn",
                        "real_unlock_type",
                        "real_once_price",
                        "real_forever_price",
                    ):
                        songs[mid][atr] = entry.find(atr).text
            break

    response = E.response(
        E.get_music_info(
            E.music_list(
                *[
                    E.music_spec(
                        E.basename("", __type="str"),
                        E.title("", __type="str"),
                        E.title_kana("", __type="str"),
                        E.artist("", __type="str"),
                        E.artist_kana("", __type="str"),
                        E.license("", __type="str"),
                        E.license_site("", __type="str"),
                        E.priority(songs[s]["priority"], __type="s8"),
                        E.category_flag(songs[s]["category_flag"], __type="s32"),
                        E.primary_category(songs[s]["primary_category"], __type="s8"),
                        E.level_normal(songs[s]["level_normal"], __type="s8"),
                        E.level_hard(songs[s]["level_hard"], __type="s8"),
                        E.level_extreme(songs[s]["level_extreme"], __type="s8"),
                        E.level_real(songs[s]["level_real"], __type="s8"),
                        E.demo_popular(songs[s]["demo_popular"], __type="bool"),
                        E.demo_bemani(songs[s]["demo_bemani"], __type="bool"),
                        E.destination_j(songs[s]["destination_j"], __type="bool"),
                        E.destination_a(songs[s]["destination_a"], __type="bool"),
                        E.destination_y(songs[s]["destination_y"], __type="bool"),
                        E.destination_k(songs[s]["destination_k"], __type="bool"),
                        E.offline(songs[s]["offline"], __type="bool"),
                        E.unlock_type(songs[s]["unlock_type"], __type="s8"),
                        E.volume_bgm(songs[s]["volume_bgm"], __type="s8"),
                        E.volume_key(songs[s]["volume_key"], __type="s8"),
                        E.start_date("2017-03-01 10:00", __type="str"),
                        E.end_date("9999-12-31 23:59", __type="str"),
                        E.expiration_date("9999-12-31 23:59", __type="str"),
                        E.description("", __type="str"),
                        index=s,
                    )
                    for s in songs
                ],
                revision=revision,
                release_code=release_code,
            ),
            E.overwrite_music_list(
                *[
                    E.music_spec(
                        E.jk_jpn(songs[s]["jk_jpn"], __type="bool"),
                        E.jk_asia(songs[s]["jk_asia"], __type="bool"),
                        E.jk_kor(songs[s]["jk_kor"], __type="bool"),
                        E.jk_idn(songs[s]["jk_idn"], __type="bool"),
                        E.unlock_type(songs[s]["unlock_type"], __type="s8"),
                        E.real_unlock_type(songs[s]["real_unlock_type"], __type="s8"),
                        E.start_date("2017-03-01 10:00", __type="str"),
                        E.end_date("9999-12-31 23:59", __type="str"),
                        E.real_once_price(songs[s]["real_once_price"], __type="s32"),
                        E.real_forever_price(
                            songs[s]["real_forever_price"], __type="s32"
                        ),
                        E.real_start_date("2017-03-01 10:00", __type="str"),
                        E.real_end_date("9999-12-31 23:59", __type="str"),
                        index=s,
                    )
                    for s in songs
                ],
                revision=revision,
                release_code=release_code,
            ),
            E.permitted_list(
                E.flag([-1] * 32, __type="s32", sheet_type="0"),
                E.flag([-1] * 32, __type="s32", sheet_type="1"),
                E.flag([-1] * 32, __type="s32", sheet_type="2"),
                E.flag([-1] * 32, __type="s32", sheet_type="3"),
            ),
            E.gamedata_flag_list(),
            E.trend_music_list(E.trend_music(music_index=1, rank=1)),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
