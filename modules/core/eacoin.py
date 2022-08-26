import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/core", tags=["eacoin"])


@router.post('/{gameinfo}/eacoin/checkin')
async def eacoin_checkin(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.eacoin(
            E.sequence(1, __type="s16"),
            E.acstatus(1, __type="u8"),
            E.acid(1, __type="str"),
            E.acname(config.arcade, __type="str"),
            E.balance(config.paseli, __type="s32"),
            E.sessid(1, __type="str"),
            E.inshopcharge(1, __type="u8"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post('/{gameinfo}/eacoin/consume')
async def eacoin_consume(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.eacoin(
            E.acstatus(0, __type="u8"),
            E.autocharge(0, __type="u8"),
            E.balance(config.paseli, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post('/{gameinfo}/eacoin/getbalance')
async def eacoin_getbalance(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.eacoin(
            E.acstatus(0, __type="u8"),
            E.balance(config.paseli, __type="s32"),
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
