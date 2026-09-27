"""Server entrypoint: banner + uvicorn."""

from __future__ import annotations

import socket
from os import name
from urllib.parse import urlunparse

import uvicorn

import config
from pyeamu import has_webui

loopback_hosts = ("localhost", config.ip, socket.gethostname())
server_addresses = [f"{host}:{config.port}" for host in loopback_hosts]
server_services_urls = [
    urlunparse(("http", addr, "/core", None, None, None)) for addr in server_addresses
]


def main() -> None:
    if name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

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
    for server_services_url in server_services_urls:
        print(f"<services>\033[92m{server_services_url}\033[0m</services>")
    print("<!-- url_slash \033[92m0\033[0m or \033[92m1\033[0m -->")
    print()
    print("\033[1mWeb Interface\033[0m:")
    if has_webui:
        for server_address in server_addresses:
            print(f"http://{server_address}/webui/")
    else:
        print("/webui missing")
        print("download it here: https://github.com/drmext/BounceTrippy/releases")
    print()
    print("\033[1mSource Repository\033[0m:")
    print("https://github.com/drmext/MonkeyBusiness")
    print()
    uvicorn.run(
        "pyeamu:app",
        host="0.0.0.0",
        port=config.port,
        reload=config.dev_reload,
    )


if __name__ == "__main__":
    main()
