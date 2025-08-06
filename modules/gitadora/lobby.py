from fastapi import APIRouter, Request, Response

from core_common import E, core_prepare_response, core_process_request

router = APIRouter(prefix="/lobby", tags=["lobby"])
router.model_whitelist = ["M32", "L33", "L32", "K33", "K32", "J33", "J32"]


host = {}


@router.post("/{gameinfo}/lobby/request")
async def gitadora_lobby_request(request: Request):
    request_info = await core_process_request(request)

    root = request_info["root"][0][0]
    address_ip = root.find("address/ip").text
    check_attestid = root.find("check/attestid").text

    if host:
        if host["ip"] != address_ip:
            response = E.response(
                E.lobby(
                    E.lobbydata(
                        E.candidate(
                            E.address(
                                E.ip(host["ip"], __type="str"),
                            ),
                            E.check(
                                E.attestid(host["attestid"], __type="str"),
                            ),
                        ),
                    ),
                )
            )

        elif host["ip"] == address_ip:
            response = E.response(E.lobby())

        del host["ip"]
        del host["attestid"]

    else:
        host["ip"] = address_ip
        host["attestid"] = check_attestid
        response = E.response(E.lobby())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
