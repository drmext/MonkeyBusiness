import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["LDJ", "KDZ", "JDZ", "JDJ", "I00", "HDD", "GLD", "FDD", "ECO", "E11", "D01", "C02"]


@router.post("/{gameinfo}/shop/getname")
async def shop_getname(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.shop(
            cls_opt=0,
            opname=config.arcade,
            pid=13,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/shop/getconvention")
async def shop_getconvention(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.shop(
            E.valid(1, __type="bool"),
            music_0=-1,
            music_1=-1,
            music_2=-1,
            music_3=-1,
            start_time=0,
            end_time=0,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/shop/sentinfo")
async def shop_sentinfo(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.shop())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/shop/sendescapepackageinfo")
async def shop_sendescapepackageinfo(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.shop(expire=1200))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
