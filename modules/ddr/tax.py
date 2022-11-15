from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["MDX"]


@router.post("/{gameinfo}/tax/get_phase")
async def tax_get_phase(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.tax(
            E.phase(0, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
