"""Compose outer bare ASGI (e-amuse) with Starlette WebUI sub-app."""

from __future__ import annotations

import json
import re
from os import path
from urllib.parse import unquote, urlencode, urlparse, urlunparse

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send
import config
import modules
import utils.card as conv
from core_common import E, EamuseError, core_prepare_response, core_process_request
from modules.registry import dispatch, iter_services

loopback = "127.0.0.1"

settings = {
    s: getattr(config, s)
    for s in (
        "ip",
        "port",
        "response_compression",
        "verbose_log",
        "arcade",
        "paseli",
        "maintenance_mode",
    )
}

# Paths handled by the Starlette WebUI / static sub-app
_WEBUI_PREFIXES = ("/webui", "/ddr", "/iidx", "/gfdm", "/config", "/conv")

_CORE_SERVICES_GET = re.compile(
    r"^/core/[^/]+/services/get/?$", re.IGNORECASE
)

# (model, slashless, request_address) -> service name -> url
_services_url_cache: dict[tuple[str, bool, str], dict[str, str]] = {}

_KEEPALIVE_URL = urlunparse(
    (
        "http",
        loopback,
        "/keepalive",
        None,
        urlencode(
            {
                "pa": loopback,
                "ia": loopback,
                "ga": loopback,
                "ma": loopback,
                "t1": 2,
                "t2": 10,
            }
        ),
        None,
    )
)
_NTP_URL = urlunparse(("ntp", "pool.ntp.org", "/", None, None, None))


def _resolve_path_key(request: Request) -> str | None:
    """Slashless (?f= / module+method) or slashed ({path}) -> module/method key."""
    qp = request.query_params
    f = qp.get("f")
    module = qp.get("module")
    method = qp.get("method")

    if f is not None:
        module, method = f.split(".", 1)

    if module and method:
        return f"{module}/{method}"

    path_params = request.scope.get("path_params") or {}
    if "path" in path_params:
        return path_params["path"]

    return None


async def handle_xrpc(request: Request, *, model: str | None = None) -> Response:
    if model is None:
        model = request.query_params.get("model")
    path_key = _resolve_path_key(request)
    if not path_key:
        return Response(status_code=404)
    return await dispatch(request, model, path_key)


def _services_for(model: str, slashless: bool, request_address: str) -> dict[str, str]:
    key = (model, slashless, request_address)
    cached = _services_url_cache.get(key)
    if cached is not None:
        return cached

    services: dict[str, str] = {}
    for service_name, prefix in iter_services(model):
        if service_name in services:
            continue
        pre = "/fwdr" if slashless else prefix
        services[service_name] = urlunparse(
            ("http", request_address, pre, None, None, None)
        )
    services["keepalive"] = _KEEPALIVE_URL
    services["ntp"] = _NTP_URL
    _services_url_cache[key] = services
    return services


async def services_get(request: Request) -> Response:
    request_info = await core_process_request(request)

    parsed = urlparse(str(request.url))
    if parsed.port is not None:
        request_address = parsed.netloc
    else:
        request_address = f"{parsed.netloc}:{config.port}"

    qp = request.query_params
    f = qp.get("f")
    module = qp.get("module")
    method = qp.get("method")
    slashless = f == "services.get" or (module == "services" and method == "get")

    services = _services_for(request_info["model"], slashless, request_address)

    response = E.response(
        E.services(
            expire=10800,
            mode="operation",
            product_domain=1,
            *[E.item(name=k, url=services[k]) for k in services],
        )
    )

    response_body, response_headers = core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


async def redirect_to_webui(request: Request) -> Response:
    return RedirectResponse(url="/webui")


async def get_config(request: Request) -> Response:
    return JSONResponse(settings)


async def card_conv(request: Request) -> Response:
    card = request.path_params["card"].upper()
    lookalike = {"I": "1", "O": "0", "Q": "0", "V": "U"}
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
    return JSONResponse({"uid": uid, "konami_id": kid})


async def redirect_webui_missing(request: Request) -> Response:
    return RedirectResponse(url="/config")


def _build_webui() -> Starlette:
    routes: list = [
        Route("/", redirect_to_webui, methods=["GET"]),
        Route("/config", get_config, methods=["GET"]),
        Route("/conv/{card}", card_conv, methods=["GET"]),
    ]

    for mount_path, api_router in modules.webui_routers:
        routes.insert(0, Mount(mount_path, app=api_router))

    if path.exists("webui"):
        with open(path.join("webui", "monkey.json"), "w") as f:
            json.dump(settings, f, indent=2)
        routes.insert(0, Mount("/webui", app=StaticFiles(directory="webui", html=True)))
    else:
        routes.insert(0, Route("/webui", redirect_webui_missing, methods=["GET"]))

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    return Starlette(routes=routes, middleware=middleware)


webui_app: ASGIApp = _build_webui()
has_webui = path.exists("webui")


async def _send_response(response: Response, scope: Scope, receive: Receive, send: Send) -> None:
    await response(scope, receive, send)


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    if scope["type"] == "lifespan":
        await webui_app(scope, receive, send)
        return

    if scope["type"] != "http":
        return

    raw_path = unquote(scope.get("path") or "")
    method = scope.get("method", "GET").upper()

    # WebUI / static / config / card converter
    if raw_path == "/" or any(
        raw_path == p or raw_path.startswith(p + "/") for p in _WEBUI_PREFIXES
    ):
        await webui_app(scope, receive, send)
        return

    if method != "POST":
        await _send_response(Response(status_code=404), scope, receive, send)
        return

    request = Request(scope, receive)

    try:
        # services.get
        if raw_path.rstrip("/") == "/core" or _CORE_SERVICES_GET.match(raw_path):
            response = await services_get(request)
        elif raw_path.rstrip("/") == "/fwdr":
            response = await handle_xrpc(request)
        else:
            # slashed: /{svc}/{gameinfo}/{path...} — model is the gameinfo segment
            parts = [p for p in raw_path.strip("/").split("/") if p]
            if len(parts) >= 3:
                scope = dict(scope)
                scope["path_params"] = {"path": "/".join(parts[2:])}
                request = Request(scope, receive)
                model = request.query_params.get("model") or parts[1]
                response = await handle_xrpc(request, model=model)
            else:
                response = Response(status_code=404)
    except EamuseError as exc:
        response = Response(status_code=exc.status_code, content=exc.detail or b"")

    await _send_response(response, scope, receive, send)
