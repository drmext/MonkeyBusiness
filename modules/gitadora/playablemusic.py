import lxml.etree as ET
from os import path

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["M32"]


@router.post("/{gameinfo}/{ver}_playablemusic/get")
async def gitadora_playablemusic_get(ver: str, request: Request):
    request_info = await core_process_request(request)

    # the game freezes if response has no songs
    # so make sure there is at least one
    # in case mdb isn't supplied
    songs = {
        0: {
            "xg_diff_list": [
                "0",
                "100",
                "295",
                "395",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "160",
                "490",
                "585",
                "0",
            ],
            "contain_stat": ["2", "2"],
            "data_ver": 115,
        }
    }

    if ver == "galaxywave":
        short_ver = "gw"
    elif ver == "fuzzup":
        short_ver = "fz"
    elif ver == "highvoltage":
        short_ver = "hv"
    elif ver == "nextage":
        short_ver = "nt"
    elif ver == "exchain":
        short_ver = "ex"
    elif ver == "matixx":
        short_ver = "mt"

    if not short_ver:
        short_ver = "MISSING_FALLBACK"

    for f in (
        path.join("modules", "gitadora", f"mdb_{short_ver}.xml"),
        path.join(f"mdb_{short_ver}.xml"),
    ):
        if path.exists(f):
            with open(f, "r", encoding="utf-8") as fp:

                tree = ET.parse(fp, ET.XMLParser())
                root = tree.getroot()

                for entry in root:
                    if entry.tag == "mdb_data":
                        lvl = entry.find("xg_diff_list").text.split(" ")
                        if short_ver in ("fz", "hv", "nt", "ex"):
                            d_ver = int(entry.find("data_ver").text)
                        else:
                            d_ver = 115

                        mid = entry.find("music_id").text
                        songs[mid] = {}
                        songs[mid]["xg_diff_list"] = lvl[:5] + lvl[10:] + lvl[5:10]
                        songs[mid]["contain_stat"] = entry.find(
                            "contain_stat"
                        ).text.split(" ")
                        songs[mid]["data_ver"] = d_ver
            break

    response = E.response(
        E(
            f"{ver}_playablemusic",
            E.hot(
                E.major(-1, __type="s32"),
                E.minor(-1, __type="s32"),
            ),
            E.musicinfo(
                *[
                    E.music(
                        E.id(s, __type="s32"),
                        E.cont_gf(
                            1 if int(songs[s]["contain_stat"][0]) != 0 else 0,
                            __type="bool",
                        ),
                        E.cont_dm(
                            1 if int(songs[s]["contain_stat"][1]) != 0 else 0,
                            __type="bool",
                        ),
                        E.is_secret(0, __type="bool"),
                        E.is_hot(
                            1
                            if (int(songs[s]["contain_stat"][0]) & 1)
                            or (int(songs[s]["contain_stat"][1]) & 1)
                            else 0,
                            __type="bool",
                        ),
                        E.data_ver(songs[s]["data_ver"], __type="s32"),
                        E.seq_release_state(1, __type="s32"),
                        E.diff(songs[s]["xg_diff_list"], __type="u16"),
                    )
                    for s in songs
                ],
                nr=len(songs),
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
