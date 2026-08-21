"""Shared fixtures.

Note how every fixture builds the object graph explicitly: because the
production code depends on ports rather than concrete classes, tests can
substitute a frozen clock or a tiny repository with no patching at all.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.container import Container
from app.domain.ports import Clock
from app.infrastructure.clock import FrozenClock
from app.infrastructure.formatters.base import DefaultFormatter
from app.infrastructure.formatters.japanese import JapaneseFormatter
from app.infrastructure.formatters.registry import FormatterRegistry
from app.infrastructure.repositories.in_memory import InMemoryGreetingTemplateRepository
from app.main import create_app
from app.services.greeting_service import GreetingService

FROZEN_MOMENT = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def settings() -> Settings:
    return Settings(environment="test", log_json=False, log_level="WARNING")


@pytest.fixture
def clock() -> Clock:
    return FrozenClock(FROZEN_MOMENT)


@pytest.fixture
def templates() -> InMemoryGreetingTemplateRepository:
    return InMemoryGreetingTemplateRepository()


@pytest.fixture
def formatters() -> FormatterRegistry:
    return FormatterRegistry(
        formatters=[DefaultFormatter(), JapaneseFormatter()],
        fallback=DefaultFormatter(),
    )


@pytest.fixture
def greeting_service(
    templates: InMemoryGreetingTemplateRepository,
    formatters: FormatterRegistry,
    clock: Clock,
) -> GreetingService:
    return GreetingService(
        templates=templates, formatters=formatters, clock=clock, default_locale="en"
    )


@pytest.fixture
def container(
    settings: Settings,
    clock: Clock,
    templates: InMemoryGreetingTemplateRepository,
    formatters: FormatterRegistry,
    greeting_service: GreetingService,
) -> Container:
    return Container(
        settings=settings,
        clock=clock,
        templates=templates,
        formatters=formatters,
        greeting_service=greeting_service,
    )


@pytest.fixture
def app(settings: Settings, container: Container) -> FastAPI:
    return create_app(settings=settings, container=container)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with (
        AsyncClient(transport=transport, base_url="http://testserver") as async_client,
    ):
        yield async_client
