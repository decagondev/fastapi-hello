"""FastAPI dependency providers.

Endpoints depend on *ports*, not concrete classes. These providers pull the
already-wired objects out of the container stored on ``app.state``, which
makes overriding them in tests a one-liner.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings
from app.core.container import Container
from app.domain.ports import GreetingUseCase


def get_container(request: Request) -> Container:
    """Return the container built during application startup."""
    container = getattr(request.app.state, "container", None)
    if container is None:  # pragma: no cover - defensive, set during startup
        msg = "Application container was not initialised."
        raise RuntimeError(msg)
    assert isinstance(container, Container)  # noqa: S101
    return container


def get_settings_dep(container: Annotated[Container, Depends(get_container)]) -> Settings:
    """Expose validated settings to endpoints."""
    return container.settings


def get_greeting_service(
    container: Annotated[Container, Depends(get_container)],
) -> GreetingUseCase:
    """Expose the greeting use case as an abstract port."""
    return container.greeting_service


ContainerDep = Annotated[Container, Depends(get_container)]
SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
GreetingServiceDep = Annotated[GreetingUseCase, Depends(get_greeting_service)]
