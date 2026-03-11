import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["MDX"]


@router.post("/{gameinfo}/wordcheck_3/tabooword_check")
async def wordcheck_3_tabooword_check(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.wordcheck_3(
            E.result(0, __type="s32"),
            E.is_taboo(0, __type="bool"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
