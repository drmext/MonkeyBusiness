"""Helpers for Starlette WebUI JSON APIs."""

from __future__ import annotations

import json
from typing import Any, Callable, Type

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


async def read_model(request: Request, model: Type[BaseModel]) -> BaseModel:
    body = await request.body()
    data = json.loads(body) if body else {}
    return model.model_validate(data)


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
