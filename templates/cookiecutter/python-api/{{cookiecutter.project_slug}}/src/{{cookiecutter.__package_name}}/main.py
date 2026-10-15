"""Application factory and ASGI entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import router
from .config import Settings
from .logging_config import configure_logging
from .middleware import install_request_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.ready = True
    try:
        yield
    finally:
        app.state.ready = False


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()
    configure_logging(resolved.log_level)

    application = FastAPI(title=resolved.app_name, lifespan=lifespan)
    application.state.ready = False
    application.include_router(router)
    install_request_middleware(application, resolved.app_name)
    return application


app = create_app()
