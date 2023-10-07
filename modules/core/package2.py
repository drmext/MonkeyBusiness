from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/core", tags=["package2"])


@router.post("/{gameinfo}/package2/list")
async def package2_list(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.package2(expire=1200, status=0))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
