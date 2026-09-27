import importlib
import pkgutil

from . import registry  # noqa: F401

webui_routers = []

_SKIP = {"registry", "webapi"}

for modinfo in pkgutil.walk_packages(__path__, __name__ + "."):
    short = modinfo.name.rsplit(".", 1)[-1]
    if short in _SKIP or short.startswith("_"):
        continue

    module = importlib.import_module(modinfo.name)

    if short == "api":
        api_router = getattr(module, "router", None)
        if api_router is not None:
            pkg = modinfo.name.split(".")[-2]  # modules.ddr.api -> ddr
            mount = {"ddr": "/ddr", "iidx": "/iidx", "gitadora": "/gfdm"}.get(pkg)
            if mount:
                webui_routers.append((mount, api_router))
