import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["LDJ"]


@router.post("/{gameinfo}/IIDX33shop/getname")
async def iidx33shop_getname(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX33shop(
            cls_opt=0,
            opname=config.arcade,
            pid=13,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX33shop/getconvention")
async def iidx33shop_getconvention(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX33shop(
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


@router.post("/{gameinfo}/IIDX33shop/sentinfo")
async def iidx33shop_sentinfo(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX33shop())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX33shop/sendescapepackageinfo")
async def iidx33shop_sendescapepackageinfo(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX33shop(expire=1200))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post("/{gameinfo}/IIDX33shop/getclosingtime")
async def iidx33shop_getclosingtime(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.IIDX33shop(
            E.exist(1, __type="bool"),
            *[E.week(cls_opt=0, week=i) for i in range(7)]
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

@router.post("/{gameinfo}/IIDX33shop/saveclosingtime")
async def iidx33shop_saveclosingtime(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX33shop())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
