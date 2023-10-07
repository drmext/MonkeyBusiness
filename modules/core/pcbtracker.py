import config

from time import time

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/core", tags=["pcbtracker"])


@router.post("/{gameinfo}/pcbtracker/alive")
async def pcbtracker_alive(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.pcbtracker(
            status=0,
            expire=1200,
            ecenable=not config.maintenance_mode,
            eclimit=0,
            limit=0,
            time=int(time()),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
