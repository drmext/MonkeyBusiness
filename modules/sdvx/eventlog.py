import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["KFC"]


@router.post("/{gameinfo}/eventlog/write")
async def sdvx_eventlog_write(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.eventlog(
            E.gamesession(9999999, __type="s64"),
            E.logsendflg(1 if config.maintenance_mode else 0, __type="s32"),
            E.logerrlevel(0, __type="s32"),
            E.evtidnosendflg(0, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
