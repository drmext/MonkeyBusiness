import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["MDX"]


@router.post('/{gameinfo}/eventlog_2/write')
async def eventlog_2_write(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.eventlog_2(
            E.gamesession(9999999, __type="s64"),
            E.logsendflg(1 if config.maintenance_mode else 0, __type="s32"),
            E.logerrlevel(0, __type="s32"),
            E.evtidnosendflg(0, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
