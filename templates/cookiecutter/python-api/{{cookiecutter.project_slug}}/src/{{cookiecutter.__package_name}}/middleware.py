"""Request correlation, timing, and structured access logging."""

from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

LOGGER = logging.getLogger("api.requests")


def _route_pattern(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else "unmatched"


def install_request_middleware(app: FastAPI, service: str) -> None:
    @app.middleware("http")
    async def request_context(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid4())
        started = perf_counter()

        try:
            response = await call_next(request)
            event = "request_completed"
            error_type: str | None = None
        except Exception as error:
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
            event = "request_failed"
            error_type = type(error).__name__

        response.headers["X-Request-ID"] = request_id
        duration_ms = round((perf_counter() - started) * 1000, 3)
        LOGGER.info(
            event,
            extra={
                "event": event,
                "service": service,
                "request_id": request_id,
                "method": request.method,
                "route": _route_pattern(request),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "error_type": error_type,
            },
        )
        return response
