from modules.registry import Ctx, set_xrpc_defaults, xrpc

from core_common import E

host = {}

set_xrpc_defaults(service="lobby", models=["M32"])

@xrpc("lobby/request")
async def gitadora_lobby_request(ctx: Ctx):

    root = ctx.info["root"][0][0]
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

    return response
