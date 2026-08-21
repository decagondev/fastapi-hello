"""Liveness and readiness probes, kept separate for Kubernetes."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import ContainerDep, SettingsDep
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse, summary="Liveness probe")
async def liveness(settings: SettingsDep) -> HealthResponse:
    """Cheap check: the process is running and can serve HTTP."""
    return HealthResponse(
        status="ok",
        service=settings.project_name,
        version=settings.version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=HealthResponse, summary="Readiness probe")
async def readiness(container: ContainerDep) -> HealthResponse:
    """Verifies downstream dependencies can actually answer."""
    locales = await container.templates.locales()
    return HealthResponse(
        status="ok" if locales else "degraded",
        service=container.settings.project_name,
        version=container.settings.version,
        environment=container.settings.environment,
    )
