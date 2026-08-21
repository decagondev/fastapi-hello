"""Composition root.

This is the single place where concrete implementations are chosen and wired
together. Every other module depends only on abstractions, so switching an
adapter (say, in-memory templates for Postgres) is a one-line change here.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.domain.ports import Clock, GreetingTemplateRepository, GreetingUseCase
from app.infrastructure.clock import SystemClock
from app.infrastructure.formatters.base import DefaultFormatter
from app.infrastructure.formatters.japanese import JapaneseFormatter
from app.infrastructure.formatters.registry import FormatterRegistry
from app.infrastructure.repositories.in_memory import InMemoryGreetingTemplateRepository
from app.services.greeting_service import GreetingService


@dataclass(frozen=True, slots=True)
class Container:
    """Holds the fully constructed object graph for one application instance."""

    settings: Settings
    clock: Clock
    templates: GreetingTemplateRepository
    formatters: FormatterRegistry
    greeting_service: GreetingUseCase


def build_container(settings: Settings) -> Container:
    """Construct the object graph. Override pieces in tests as needed."""
    clock: Clock = SystemClock()
    templates: GreetingTemplateRepository = InMemoryGreetingTemplateRepository()
    formatters = FormatterRegistry(
        formatters=[DefaultFormatter(), JapaneseFormatter()],
        fallback=DefaultFormatter(),
    )
    greeting_service: GreetingUseCase = GreetingService(
        templates=templates,
        formatters=formatters,
        clock=clock,
        default_locale=settings.default_locale,
    )
    return Container(
        settings=settings,
        clock=clock,
        templates=templates,
        formatters=formatters,
        greeting_service=greeting_service,
    )
