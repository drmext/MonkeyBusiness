from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["M32"]


@router.post("/{gameinfo}/{ver}_shopinfo/regist")
async def gitadora_shopinfo_regist(ver: str, request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E(
            f"{ver}_shopinfo",
            E.data(
                E.cabid(1, __type="u32"),
                E.locationid("EA000001", __type="str"),
                E.is_send(0, __type="u8"),
            ),
            E.temperature(
                E.is_send(0, __type="bool"),
            ),
            E.tax(
                E.tax_phase(1, __type="s32"),
            ),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
