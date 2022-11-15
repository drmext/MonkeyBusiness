from urllib.parse import urlunparse, urlencode

import uvicorn

from fastapi import FastAPI, Request, Response

import config
import modules

from core_common import core_process_request, core_prepare_response, E


def urlpathjoin(parts, sep="/"):
    return sep + sep.join([x.lstrip(sep) for x in parts])


server_address = f"{config.ip}:{config.port}"
server_services_url = urlunparse(
    ("http", server_address, config.services_prefix, None, None, None)
)
keepalive_address = "127.0.0.1"

app = FastAPI()
for router in modules.routers:
    app.include_router(router)


if __name__ == "__main__":
    print("https://github.com/drmext/MonkeyBusiness")
    print(" __  __             _              ")
    print("|  \/  | ___  _ __ | | _____ _   _ ")
    print("| |\/| |/ _ \| '_ \| |/ / _ \ | | |")
    print("| |  | | (_) | | | |   <  __/ |_| |")
    print("|_|  |_|\___/|_| |_|_|\_\___|\__, |")
    print("                             |___/ ")
    print(" ____            _                 ")
    print("| __ ) _   _ ___(_)_ __   ___  ___ ___ ")
    print("|  _ \| | | / __| | '_ \ / _ \/ __/ __|")
    print("| |_) | |_| \__ \ | | | |  __/\__ \__ \\")
    print("|____/ \__,_|___/_|_| |_|\___||___/___/")
    print()
    print(f"<services>{server_services_url}</services>")
    print('<url_slash __type="bool">1</url_slash>')
    print()
    uvicorn.run("pyeamu:app", host=config.ip, port=config.port, reload=True)


@app.post(urlpathjoin([config.services_prefix, "/{gameinfo}/services/get"]))
async def services_get(request: Request):
    request_info = await core_process_request(request)

    services = {}

    for service in modules.routers:
        model_blacklist = services.get("model_blacklist", [])
        model_whitelist = services.get("model_whitelist", [])

        if request_info["model"] in model_blacklist:
            continue

        if model_whitelist and request_info["model"] not in model_whitelist:
            continue

        k = (service.tags[0] if service.tags else service.prefix).strip("/")
        if k not in services:
            services[k] = urlunparse(
                ("http", server_address, service.prefix, None, None, None)
            )

    keepalive_params = {
        "pa": keepalive_address,
        "ia": keepalive_address,
        "ga": keepalive_address,
        "ma": keepalive_address,
        "t1": 2,
        "t2": 10,
    }
    services["keepalive"] = urlunparse(
        (
            "http",
            keepalive_address,
            "/keepalive",
            None,
            urlencode(keepalive_params),
            None,
        )
    )
    services["ntp"] = urlunparse(("ntp", "pool.ntp.org", "/", None, None, None))
    services["services"] = urlunparse(
        ("http", server_address, "/core", None, None, None)
    )

    response = E.response(
        E.services(
            expire=10800,
            mode="operation",
            product_domain=1,
            *[E.item(name=k, url=services[k]) for k in services],
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)
