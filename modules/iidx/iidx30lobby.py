from time import time

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/lobby", tags=["lobby"])
router.model_whitelist = ["LDJ"]


host = {}


@router.post("/{gameinfo}/IIDX30lobby/entry")
async def iidx30lobby_entry(request: Request):
    request_info = await core_process_request(request)

    root = request_info["root"][0]
    sp_dp = root.find("play_style").text
    arena_class = root.find("arena_class").text
    ga = root.find("address/ga").text.split()
    gp = root.find("address/gp").text
    la = root.find("address/la").text.split()

    if host and time() < host["time"]:
        # test menu reset
        if host["ga"] == ga:
            is_host = 1
            host["time"] = time() + 30
        else:
            is_host = 0
        response = E.response(
            E.IIDX30lobby(
                E.host(is_host, __type="bool"),
                E.matching_class(arena_class, __type="s32"),
                E.address(
                    E.ga(host["ga"], __type="u8"),
                    E.gp(host["gp"], __type="u16"),
                    E.la(host["la"], __type="u8"),
                ),
            )
        )
    else:
        host["ga"] = ga
        host["gp"] = gp
        host["la"] = la
        host["time"] = time() + 30
        response = E.response(
            E.IIDX30lobby(
                E.host(1, __type="bool"),
                E.matching_class(arena_class, __type="s32"),
                E.address(
                    E.ga(ga, __type="u8"),
                    E.gp(gp, __type="u16"),
                    E.la(la, __type="u8"),
                ),
            )
        )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX30lobby/update")
async def iidx30lobby_update(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX30lobby/delete")
async def iidx30lobby_delete(request: Request):
    request_info = await core_process_request(request)

    # normal reset
    del host["ga"]
    del host["gp"]
    del host["la"]
    del host["time"]
    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX30lobby/bplbattle_entry")
async def iidx30lobby_bplbattle_entry(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX30lobby/bplbattle_update")
async def iidx30lobby_bplbattle_update(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX30lobby/bplbattle_delete")
async def iidx30lobby_bplbattle_delete(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
