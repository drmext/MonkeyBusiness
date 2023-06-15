from time import time

import config

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E

router = APIRouter(prefix="/lobby", tags=["lobby"])
router.model_whitelist = ["LDJ"]


arena_host = {}
bpl_host = {}


@router.post("/{gameinfo}/IIDX30lobby/entry")
async def iidx30lobby_entry(request: Request):
    request_info = await core_process_request(request)

    root = request_info["root"][0]
    sp_dp = root.find("play_style").text
    arena_class = root.find("arena_class").text
    ga = root.find("address/ga").text.split()
    gp = root.find("address/gp").text
    la = root.find("address/la").text.split()

    if arena_host and time() < arena_host["time"]:
        # test menu reset
        if arena_host["ga"] == ga:
            is_arena_host = 1
            arena_host["time"] = time() + 30
        else:
            is_arena_host = 0
        response = E.response(
            E.IIDX30lobby(
                E.host(is_arena_host, __type="bool"),
                E.matching_class(arena_class, __type="s32"),
                E.address(
                    E.ga(arena_host["ga"], __type="u8"),
                    E.gp(arena_host["gp"], __type="u16"),
                    E.la(arena_host["la"], __type="u8"),
                ),
            )
        )
    else:
        arena_host["ga"] = ga
        arena_host["gp"] = gp
        arena_host["la"] = la
        arena_host["time"] = time() + 30
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
    del arena_host["ga"]
    del arena_host["gp"]
    del arena_host["la"]
    del arena_host["time"]
    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX30lobby/bplbattle_entry")
async def iidx30lobby_bplbattle_entry(request: Request):
    request_info = await core_process_request(request)

    root = request_info["root"][0]
    sp_dp = root.find("play_style").text
    arena_class = root.find("arena_class").text
    password = root.find("passward").text  # passward
    ga = root.find("address/ga").text.split()
    gp = root.find("address/gp").text
    la = root.find("address/la").text.split()

    if bpl_host and password in bpl_host and time() < bpl_host[password]["time"]:
        # test menu reset
        if bpl_host[password]["ga"] == ga:
            is_bpl_host = 1
            bpl_host[password]["time"] = time() + 30
        else:
            is_bpl_host = 0
        response = E.response(
            E.IIDX30lobby(
                E.host(is_bpl_host, __type="bool"),
                E.matching_class(arena_class, __type="s32"),
                E.address(
                    E.ga(bpl_host[password]["ga"], __type="u8"),
                    E.gp(bpl_host[password]["gp"], __type="u16"),
                    E.la(bpl_host[password]["la"], __type="u8"),
                ),
            )
        )
    else:
        bpl_host[password] = {}
        bpl_host[password]["ga"] = ga
        bpl_host[password]["gp"] = gp
        bpl_host[password]["la"] = la
        bpl_host[password]["time"] = time() + 30
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


@router.post("/{gameinfo}/IIDX30lobby/bplbattle_update")
async def iidx30lobby_bplbattle_update(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/IIDX30lobby/bplbattle_delete")
async def iidx30lobby_bplbattle_delete(request: Request):
    request_info = await core_process_request(request)

    root = request_info["root"][0]
    ga = root.find("address/ga").text.split()

    # normal reset
    for host in bpl_host:
        if bpl_host[host]["ga"] == ga:
            del bpl_host[host]
            break
    response = E.response(E.IIDX30lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
