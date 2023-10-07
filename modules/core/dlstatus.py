from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/core", tags=["dlstatus"])


@router.post("/{gameinfo}/dlstatus/done")
async def dlstatus_done(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.dlstatus(status=0))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/dlstatus/progress")
async def dlstatus_progress(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.dlstatus(status=0))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
