"""HTTP routes exposed by the example API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status
from pydantic import BaseModel

router = APIRouter()


class StatusResponse(BaseModel):
    status: str


class HelloResponse(BaseModel):
    message: str


@router.get("/health/live", response_model=StatusResponse, tags=["health"])
async def live() -> StatusResponse:
    return StatusResponse(status="ok")


@router.get(
    "/health/ready",
    response_model=StatusResponse,
    responses={503: {"model": StatusResponse}},
    tags=["health"],
)
async def ready(request: Request, response: Response) -> StatusResponse:
    if not bool(getattr(request.app.state, "ready", False)):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return StatusResponse(status="not_ready")
    return StatusResponse(status="ready")


@router.get("/api/v1/hello", response_model=HelloResponse, tags=["example"])
async def hello(
    name: Annotated[str, Query(min_length=1, max_length=80)] = "world",
) -> HelloResponse:
    return HelloResponse(message=f"Hello, {name}!")
