import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/core", tags=["message"])


@router.post("/{gameinfo}/message/get")
async def message_get(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.message(
            expire=300,
            *[
                E.item(
                    name=s,
                    start=0,
                    end=604800,
                )
                for s in ("sys.mainte", "sys.eacoin.mainte")
                if config.maintenance_mode
            ]
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
