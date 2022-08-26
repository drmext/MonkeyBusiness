import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/core", tags=["facility"])


@router.post('/{gameinfo}/facility/get')
async def facility_get(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.facility(
            E.location(
                E('id', 'EA000001', __type="str"),
                E.country('JP', __type="str"),
                E.region('JP-13', __type="str"),
                E.customercode('X000000001', __type="str"),
                E.companycode('X000000001', __type="str"),
                E.latitude(0, __type="s32"),
                E.longitude(0, __type="s32"),
                E.accuracy(0, __type="u8"),
                E.countryname('Japan', __type="str"),
                E.regionname('Tokyo', __type="str"),
                E.countryjname('日本国', __type="str"),
                E.regionjname('東京都', __type="str"),
                E.name(config.arcade, __type="str"),
                E('type', 255, __type="u8"),
            ),
            E.line(
                E('class', 8, __type="u8"),
                E.rtt(500, __type="u16"),
                E.upclass(8, __type="u8"),
                E('id', 3, __type="str"),
            ),
            E.portfw(
                E.globalip(config.ip, __type="ip4"),
                E.globalport(5704, __type="u16"),
                E.privateport(5705, __type="u16"),
            ),
            E.public(
                E.flag(0, __type="u8"),
                E.name(config.arcade, __type="str"),
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
                    E.eapass('www.ea-pass.konami.net', __type="str"),
                    E.arcadefan('www.konami.jp/am', __type="str"),
                    E.konaminetdx('http://am.573.jp', __type="str"),
                    E.konamiid('https://id.konami.net', __type="str"),
                    E.eagate('http://eagate.573.jp', __type="str"),
                ),
            ),
            expire=10800,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
