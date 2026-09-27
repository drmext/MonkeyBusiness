"""Unified xrpc route registry for slash and slashless dispatch."""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence, Union

from starlette.requests import Request
from starlette.responses import Response

from core_common import core_prepare_response, core_process_request

ServiceArg = Union[str, Sequence[str]]

DEFAULT_PREFIX: dict[str, str] = {
    "local": "/local",
    "local2": "/local2",
    "lobby": "/lobby",
    "lobby2": "/lobby2",
    "apsmanager": "/core",
    "cardmng": "/core",
    "dlstatus": "/core",
    "eacoin": "/core",
    "facility": "/core",
    "ins": "/core",
    "message": "/core",
    "package": "/core",
    "package2": "/core",
    "pcbevent": "/core",
    "pcbtracker": "/core",
}

_PARAM_RE = re.compile(r"\{([^}/]+)\}")


@dataclass
class Ctx:
    """Per-request context passed to xrpc handlers."""

    request: Request
    info: dict


@dataclass
class RouteEntry:
    regex: Optional[re.Pattern]
    template: str
    endpoint: Callable
    param_names: list[str]
    whitelist: Optional[frozenset]
    blacklist: frozenset
    services: list[tuple[str, str]] = field(default_factory=list)


_module_defaults: dict[str, dict[str, Any]] = {}
_static: dict[str, list[RouteEntry]] = {}
_param: list[RouteEntry] = []
_services: list[tuple[str, str, Optional[frozenset], frozenset]] = []


def set_xrpc_defaults(
    *,
    service: Optional[ServiceArg] = None,
    prefix: Optional[Union[str, Sequence[str]]] = None,
    models: Optional[Sequence[str]] = None,
    model_blacklist: Optional[Sequence[str]] = None,
) -> None:
    """Set default @xrpc kwargs for the calling module."""
    modname = inspect.currentframe().f_back.f_globals.get("__name__", "")
    defaults: dict[str, Any] = {}
    if service is not None:
        defaults["service"] = service
    if prefix is not None:
        defaults["prefix"] = prefix
    if models is not None:
        defaults["models"] = models
    if model_blacklist is not None:
        defaults["model_blacklist"] = model_blacklist
    _module_defaults[modname] = defaults


def _path_template_regex(template: str) -> re.Pattern:
    parts = []
    last = 0
    for param in _PARAM_RE.finditer(template):
        parts.append(re.escape(template[last : param.start()]))
        parts.append(f"(?P<{param.group(1)}>[^/]+)")
        last = param.end()
    parts.append(re.escape(template[last:]))
    return re.compile("^" + "".join(parts) + "$", re.IGNORECASE)


def _normalize_services(
    service: ServiceArg, prefix: Optional[Union[str, Sequence[str]]]
) -> list[tuple[str, str]]:
    if isinstance(service, str):
        names = [service]
    else:
        names = list(service)

    if prefix is None:
        prefixes = [DEFAULT_PREFIX.get(n, f"/{n}") for n in names]
    elif isinstance(prefix, str):
        prefixes = [prefix] * len(names)
    else:
        prefixes = list(prefix)
        if len(prefixes) != len(names):
            raise ValueError("prefix sequence must match service names")

    return list(zip(names, prefixes))


def _model_allowed(
    model_code: str, whitelist: Optional[frozenset], blacklist: frozenset
) -> bool:
    if model_code in blacklist:
        return False
    if whitelist is not None and model_code not in whitelist:
        return False
    return True


async def _finish(request: Request, result: Any) -> Response:
    if isinstance(result, Response):
        return result
    body, headers = core_prepare_response(request, result)
    return Response(content=body, headers=headers)


def _make_endpoint(fn: Callable, user_params: list[str]) -> Callable:
    """Build a process/prepare wrapper specialized for common handler shapes."""

    # Most handlers: async def handler(ctx: Ctx)
    if user_params == ["ctx"]:

        async def endpoint_ctx(request: Request, **_captures: str) -> Response:
            info = await core_process_request(request)
            return await _finish(
                request, await fn(Ctx(request=request, info=info))
            )

        return endpoint_ctx

    # Parameterized: async def handler(ver|player|..., ctx: Ctx)
    if len(user_params) == 2 and user_params[1] == "ctx":
        cap_name = user_params[0]

        async def endpoint_cap(request: Request, **captures: str) -> Response:
            info = await core_process_request(request)
            return await _finish(
                request,
                await fn(captures[cap_name], Ctx(request=request, info=info)),
            )

        return endpoint_cap

    async def endpoint_general(request: Request, **captures: str) -> Response:
        info = await core_process_request(request)
        ctx = Ctx(request=request, info=info)
        kwargs: dict[str, Any] = {}
        for name in user_params:
            if name == "ctx":
                kwargs["ctx"] = ctx
            elif name in captures:
                kwargs[name] = captures[name]
        return await _finish(request, await fn(**kwargs))

    return endpoint_general


def xrpc(
    template: str,
    *,
    service: Optional[ServiceArg] = None,
    prefix: Optional[Union[str, Sequence[str]]] = None,
    models: Optional[Sequence[str]] = None,
    model_blacklist: Optional[Sequence[str]] = None,
) -> Callable:
    """Register an e-amuse handler; wraps process/prepare around the function."""

    modname = inspect.currentframe().f_back.f_globals.get("__name__", "")
    defaults = _module_defaults.get(modname, {})
    if service is None:
        service = defaults.get("service")
    if service is None:
        raise TypeError("@xrpc requires service= or set_xrpc_defaults(service=...)")
    if prefix is None:
        prefix = defaults.get("prefix")
    if models is None and "models" in defaults:
        models = defaults["models"]
    if model_blacklist is None and "model_blacklist" in defaults:
        model_blacklist = defaults["model_blacklist"]

    template = template.lstrip("/")
    pairs = _normalize_services(service, prefix)
    whitelist = frozenset(models) if models is not None else None
    blacklist = frozenset(model_blacklist) if model_blacklist else frozenset()
    parameterized = "{" in template

    def decorator(fn: Callable) -> Callable:
        user_params = list(inspect.signature(fn).parameters.keys())
        endpoint = _make_endpoint(fn, user_params)

        entry = RouteEntry(
            regex=_path_template_regex(template) if parameterized else None,
            template=template,
            endpoint=endpoint,
            param_names=user_params,
            whitelist=whitelist,
            blacklist=blacklist,
            services=pairs,
        )
        if parameterized:
            _param.append(entry)
        else:
            _static.setdefault(template.lower(), []).append(entry)
        for name, pref in pairs:
            _services.append((name, pref, whitelist, blacklist))
        return fn

    return decorator


def clear() -> None:
    _static.clear()
    _param.clear()
    _services.clear()
    _module_defaults.clear()


def routes() -> list[RouteEntry]:
    out: list[RouteEntry] = []
    for entries in _static.values():
        out.extend(entries)
    out.extend(_param)
    return out


async def dispatch(
    request: Request, model: Optional[str], path_key: str
) -> Response:
    model_code = (model or "").split(":")[0]
    path_key = path_key.lstrip("/")

    for entry in _static.get(path_key.lower(), ()):
        if not _model_allowed(model_code, entry.whitelist, entry.blacklist):
            continue
        return await entry.endpoint(request)

    for entry in _param:
        if not _model_allowed(model_code, entry.whitelist, entry.blacklist):
            continue
        match = entry.regex.match(path_key)
        if not match:
            continue
        return await entry.endpoint(request, **match.groupdict())

    return Response(status_code=404)


def iter_services(model_code: str) -> list[tuple[str, str]]:
    """Unique (service_name, prefix) advertised for this game model code."""
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for name, pref, whitelist, blacklist in _services:
        if not _model_allowed(model_code, whitelist, blacklist):
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append((name, pref))
    return out
