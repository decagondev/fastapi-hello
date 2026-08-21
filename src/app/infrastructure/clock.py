"""Concrete :class:`app.domain.ports.Clock` adapters."""

from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """Returns the real, timezone-aware current time."""

    def now(self) -> datetime:
        """Return the current UTC time."""
        return datetime.now(tz=UTC)


class FrozenClock:
    """A deterministic clock, useful in tests and demos."""

    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        """Return the fixed moment this clock was created with."""
        return self._moment
