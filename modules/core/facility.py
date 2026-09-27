from modules.registry import Ctx, set_xrpc_defaults, xrpc
import config

from tinydb import where

from core_common import E
from core_database import get_db

set_xrpc_defaults(service="facility")

@xrpc("facility/get")
async def facility_get(ctx: Ctx):
    pcbid = ctx.info["root"].attrib["srcid"]

    op = get_db().table("shop").get(where("pcbid") == pcbid)
    op = {} if op is None else op

    response = E.response(
        E.facility(
            E.location(
                E("id", "EA000001", __type="str"),
                E.country("JP", __type="str"),
                E.region("JP-13", __type="str"),
                E.customercode("X000000001", __type="str"),
                E.companycode("X000000001", __type="str"),
                E.latitude(0, __type="s32"),
                E.longitude(0, __type="s32"),
                E.accuracy(0, __type="u8"),
                E.countryname("Japan", __type="str"),
                E.regionname("Tokyo", __type="str"),
                E.countryjname("日本国", __type="str"),
                E.regionjname("東京都", __type="str"),
                E.name(op.get("opname", config.arcade), __type="str"),
                E("type", 255, __type="u8"),
            ),
            E.line(
                E("class", 8, __type="u8"),
                E.rtt(500, __type="u16"),
                E.upclass(8, __type="u8"),
                E("id", 3, __type="str"),
            ),
            E.portfw(
                E.globalip(ctx.request.client.host, __type="ip4"),
                E.globalport(5700, __type="u16"),
                E.privateport(5700, __type="u16"),
            ),
            E.public(
                E.flag(1, __type="u8"),
                E.name(op.get("opname", config.arcade), __type="str"),
                E.latitude(0, __type="str"),
                E.longitude(0, __type="str"),
            ),
            E.share(
                E.eacoin(
                    E.notchamount(3000, __type="s32"),
                    E.notchcount(3, __type="s32"),
                    E.supplylimit(9999, __type="s32"),
                ),
                E.eapass(
                    E.valid(365, __type="u16"),
                ),
                E.url(
                    E.eapass("www.ea-pass.konami.net", __type="str"),
                    E.arcadefan("www.konami.jp/am", __type="str"),
                    E.konaminetdx("http://am.573.jp", __type="str"),
                    E.konamiid("https://id.konami.net", __type="str"),
                    E.eagate("http://eagate.573.jp", __type="str"),
                ),
            ),
            expire=10800,
        )
    )

    return response
