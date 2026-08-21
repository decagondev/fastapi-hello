"""Ports (abstract interfaces) for the application.

Every port here is a :class:`typing.Protocol`, which gives us structural
typing: implementations in ``app.infrastructure`` never import these classes
at runtime, yet mypy still verifies they satisfy the contract.

* **Dependency Inversion** -- ``app.services`` depends on these abstractions,
  never on concrete adapters.
* **Interface Segregation** -- each protocol is deliberately tiny, so no
  implementation is forced to provide methods it does not need.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from app.domain.models import Greeting, GreetingTemplate


@runtime_checkable
class Clock(Protocol):
    """Supplies the current time. Injected so tests can freeze it."""

    def now(self) -> datetime:
        """Return the current, timezone-aware time."""
        ...


@runtime_checkable
class GreetingTemplateRepository(Protocol):
    """Read-only access to greeting templates."""

    async def get(self, locale: str) -> GreetingTemplate | None:
        """Return the template for ``locale``, or ``None`` if unknown."""
        ...

    async def locales(self) -> tuple[str, ...]:
        """Return every locale this repository can serve, sorted."""
        ...


@runtime_checkable
class GreetingFormatter(Protocol):
    """Locale-specific post-processing strategy for a rendered greeting.

    New locales with special rules are added by writing a new formatter and
    registering it -- existing code is never edited (Open/Closed Principle).
    """

    @property
    def locale(self) -> str:
        """Return the locale this formatter is responsible for."""
        ...

    def format(self, template: GreetingTemplate, recipient: str) -> str:
        """Return the finished greeting text."""
        ...


@runtime_checkable
class FormatterResolver(Protocol):
    """Selects the formatter to use for a locale.

    The service depends on this rather than on the concrete registry, so the
    resolution strategy (static map, plugin discovery, remote config) can
    change without touching the use case.
    """

    def resolve(self, locale: str) -> GreetingFormatter:
        """Return the formatter for ``locale``, never ``None``."""
        ...


@runtime_checkable
class GreetingUseCase(Protocol):
    """The inbound port the API layer talks to."""

    async def greet(self, recipient: str, locale: str | None = None) -> Greeting:
        """Return a greeting for ``recipient``, raising ``DomainError`` on failure."""
        ...

    async def supported_locales(self) -> tuple[str, ...]:
        """Return every locale that can currently be served."""
        ...
