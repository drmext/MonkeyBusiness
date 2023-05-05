from urllib.parse import urlunparse, urlencode

import uvicorn

import ujson as json
from os import name, path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

import config
import modules
import utils.card as conv

from core_common import core_process_request, core_prepare_response, E


def urlpathjoin(parts, sep="/"):
    return sep + sep.join([x.lstrip(sep) for x in parts])


server_address = f"{config.ip}:{config.port}"
server_services_url = urlunparse(
    ("http", server_address, config.services_prefix, None, None, None)
)
keepalive_address = "127.0.0.1"

settings = {}
for s in (
    "ip",
    "port",
    "services_prefix",
    "verbose_log",
    "arcade",
    "paseli",
    "maintenance_mode",
):
    settings[s] = getattr(config, s)

app = FastAPI()
for router in modules.routers:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if path.exists("webui"):
    webui = True
    with open(path.join("webui", "monkey.json"), "w") as f:
        json.dump(settings, f, indent=2, escape_forward_slashes=False)
    app.mount("/webui", StaticFiles(directory="webui", html=True), name="webui")
else:
    webui = False

    @app.get("/webui")
    async def redirect_to_config():
        return RedirectResponse(url="/config")


# Enable ANSI escape sequences
if name == "nt":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


if __name__ == "__main__":
    print(
        """
 █▄ ▄█ █▀█ █▄ █ █▄▀ ▀██ ▀▄▀
 █ ▀ █ █▄█ █ ▀█ █ █ ▄▄█  █

 ██▄ █ █ ▄▀▀ ▄█ █▄ █ ▀██ ▀█▀
 █▄█ ▀▄█ ▄██  █ █ ▀█ ▄▄█ █▄▄
"""
    )
    print()
    print("\033[1mGame Config\033[0m:")
    print(f"<services>\033[92m{server_services_url}\033[0m</services>")
    print('<url_slash __type="bool">\033[92m1\033[0m</url_slash>')
    print()
    if webui:
        print("\033[1mWeb Interface\033[0m:")
        print(f"http://{server_address}/webui/")
        print()
    print("\033[1mSource Repository\033[0m:")
    print("https://github.com/drmext/MonkeyBusiness")
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


@app.get("/")
async def redirect_to_webui():
    return RedirectResponse(url="/webui")


@app.get("/config")
async def get_config():
    return settings


@app.get("/conv/{card}")
async def card_conv(card: str):
    card = card.upper()
    lookalike = {
        "I": "1",
        "O": "0",
        "Q": "0",
        "V": "U",
    }
    for k, v in lookalike.items():
        card = card.replace(k, v)
    if card.startswith("E004") or card.startswith("012E"):
        card = "".join([c for c in card if c in "0123456789ABCDEF"])
        uid = card
        kid = conv.to_konami_id(card)
    else:
        card = "".join([c for c in card if c in conv.valid_characters])
        uid = conv.to_uid(card)
        kid = card
    return {"uid": uid, "konami_id": kid}
