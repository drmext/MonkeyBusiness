import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["REC"]


@router.post("/{gameinfo}/eventlog/write")
async def drs_eventlog_write(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.eventlog(
            E.gamesession(9999999, __type="s64"),
            E.logsendflg(0, __type="s32"),
            E.logerrlevel(0, __type="s32"),
            E.evtidnosendflg(0, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
