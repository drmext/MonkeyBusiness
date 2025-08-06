import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["LDJ", "KDZ", "JDZ", "JDJ", "I00", "HDD", "GLD", "FDD", "ECO", "E11", "D01", "C02"]


@router.post("/{gameinfo}/ranking/getranker")
async def ranking_getranker(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.ranking())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
