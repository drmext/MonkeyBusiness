from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/core", tags=["ins"])


@router.post("/{gameinfo}/ins/netlog")
async def ins_netlog(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.netlog(status=0))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/ins/send")
async def ins_send(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.netlog(status=0))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
