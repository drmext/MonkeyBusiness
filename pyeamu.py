from urllib.parse import urlunparse, urlencode

import uvicorn

import ujson as json
from os import path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

import config
import modules
import utils.card as conv

from core_common import core_process_request, core_prepare_response, E

from modules.core.pcbtracker import pcbtracker_alive
from modules.core.message import message_get
from modules.core.facility import facility_get
from modules.core.package import package_list
from modules.core.pcbevent import pcbevent_put
from modules.core.cardmng import cardmng_inquire
from modules.core.cardmng import cardmng_authpass
from modules.core.cardmng import cardmng_bindmodel
from modules.core.cardmng import cardmng_getrefid

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
        json.dump(settings, f, indent=2)
    app.mount("/webui", StaticFiles(directory="webui", html=True), name="webui")
else:
    webui = False

    @app.get("/webui")
    async def redirect_to_config():
        return RedirectResponse(url="/config")


if __name__ == "__main__":
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
    print("Game Config:")
    print(f"<services>{server_services_url}</services>")
    print('<url_slash __type="bool">1</url_slash>')
    print()
    if webui:
        print("Web Interface:")
        print(f"http://{server_address}/webui/")
        print()
    print("Source Repository:")
    print("https://github.com/drmext/MonkeyBusiness")
    print()
    uvicorn.run("pyeamu:app", host=config.ip, port=config.port, reload=True)


@app.post(urlpathjoin([config.services_prefix]))
async def services_get_pop(model: Request, module: str, method: str):

    if module == "pcbtracker":
        return await pcbtracker_alive(model)
    elif module == "message":
        return await message_get(model)
    elif module == "facility":
        return await facility_get(model)
    elif module == "package":
        return await package_list(model)
    elif module == "pcbevent":
        return await pcbevent_put(model)
    elif module == "cardmng":
        if method == "inquire":
            return await cardmng_inquire(model)
        elif method == "getrefid":
            return await cardmng_getrefid(model)
        elif method == "bindmodel":
            return await cardmng_bindmodel(model)
        elif method == "authpass":
            return await cardmng_authpass(model)
    elif module == "services":
        services_get(model)
    else:
        return


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

# TODO: Answer /local2 calls, create responses and apropriate functions to go with them
#@app.post("/local2")
#async def local_two(model: Request, module: str):
#    
#    #if module == "pcb24":
     # Straight up broken. I was unable to translate the incoming XML,
     # seems like part of it is missing or jumbled. It also however seems
     # like you dont really need it? That is the conclusion for now.
     # (And I know its compressed, still nothing useful) 

#    # To be implemented
#    if module == "player24":
#        request_info = await core_process_request(model)
#        return
#    