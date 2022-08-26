import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local2", tags=["local2"])
router.model_whitelist = ["LDJ"]


@router.post('/{gameinfo}/IIDX29shop/getname')
async def iidx29shop_getname(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29shop(
            cls_opt=0,
            opname=config.arcade,
            pid=13,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post('/{gameinfo}/IIDX29shop/getconvention')
async def iidx29shop_getconvention(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29shop(
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


@router.post('/{gameinfo}/IIDX29shop/sentinfo')
async def iidx29shop_sentinfo(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29shop()
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post('/{gameinfo}/IIDX29shop/sendescapepackageinfo')
async def iidx29shop_sendescapepackageinfo(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX29shop(
            expire=1200
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
