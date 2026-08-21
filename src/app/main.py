"""Application factory.

``create_app`` is a factory rather than a module-level singleton so tests can
build isolated instances with overridden settings or containers.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router_v1
from app.core.config import Settings, get_settings
from app.core.container import Container, build_container
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.timing import TimingMiddleware
from app.schemas.health import ServiceInfoResponse

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    """Build a fully configured application instance."""
    resolved_settings = settings or get_settings()
    configure_logging(level=resolved_settings.log_level, json_output=resolved_settings.log_json)
    resolved_container = container or build_container(resolved_settings)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        """Own the lifetime of resources that must be opened and closed."""
        logger.info("%s %s starting", resolved_settings.project_name, resolved_settings.version)
        yield
        logger.info("%s shutting down", resolved_settings.project_name)

    docs_url = "/docs" if resolved_settings.docs_enabled else None
    app = FastAPI(
        title=resolved_settings.project_name,
        version=resolved_settings.version,
        debug=resolved_settings.debug,
        docs_url=docs_url,
        redoc_url="/redoc" if resolved_settings.docs_enabled else None,
        openapi_url="/openapi.json" if resolved_settings.docs_enabled else None,
        lifespan=lifespan,
    )

    # Middleware runs bottom-up: request id is outermost so timing logs carry it.
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestContextMiddleware)
    if resolved_settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved_settings.cors_origins),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Attached eagerly (not in lifespan) so the container is available to any
    # transport, including test clients that never trigger startup events.
    app.state.container = resolved_container

    register_exception_handlers(app)
    app.include_router(api_router_v1, prefix=resolved_settings.api_v1_prefix)

    @app.get("/", tags=["meta"], response_model=ServiceInfoResponse, summary="Service info")
    async def service_info() -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service=resolved_settings.project_name,
            version=resolved_settings.version,
            docs_url=docs_url,
            api_prefix=resolved_settings.api_v1_prefix,
        )

    return app


app = create_app()
