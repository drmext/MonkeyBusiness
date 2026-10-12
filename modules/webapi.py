"""Helpers for Starlette WebUI JSON APIs."""

from __future__ import annotations

import json
from dataclasses import fields
from typing import Any, Callable, Type, TypeVar

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Music-data uploads are held in memory, so reject anything larger than this.
MAX_UPLOAD_BYTES = 128 * 1024 * 1024

T = TypeVar("T")


async def read_model(request: Request, model: Type[T]) -> T:
    body = await request.body()
    data = json.loads(body) if body else {}
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    names = {field.name for field in fields(model)}
    return model(**{key: value for key, value in data.items() if key in names})


def as_response(value: Any) -> Response:
    if isinstance(value, Response):
        return value
    return JSONResponse(value)


def endpoint(fn: Callable) -> Callable:
    """Wrap an async handler so plain dict/list returns become JSON."""

    async def wrapper(request: Request) -> Response:
        result = await fn(request)
        return as_response(result)

    wrapper.__name__ = getattr(fn, "__name__", "endpoint")
    return wrapper
