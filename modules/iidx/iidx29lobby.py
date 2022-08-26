import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["LDJ"]


@router.post('/{gameinfo}/IIDX29lobby/entry')
async def iidx29lobby_entry(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29lobby()
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post('/{gameinfo}/IIDX29lobby/update')
async def iidx29lobby_update(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29lobby()
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post('/{gameinfo}/IIDX29lobby/delete')
async def iidx29lobby_delete(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29lobby()
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post('/{gameinfo}/IIDX29lobby/bplbattle_entry')
async def iidx29lobby_bplbattle_entry(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29lobby()
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post('/{gameinfo}/IIDX29lobby/bplbattle_update')
async def iidx29lobby_bplbattle_update(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29lobby()
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post('/{gameinfo}/IIDX29lobby/bplbattle_delete')
async def iidx29lobby_bplbattle_delete(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29lobby()
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
