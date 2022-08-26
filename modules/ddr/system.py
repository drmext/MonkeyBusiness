from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["MDX"]


@router.post('/{gameinfo}/system/convcardnumber')
async def system_convcardnumber(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.system(
            E.data(E.card_number('FFFFFFFFFFFFFFFF', __type="str")),
            E.result(0, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
