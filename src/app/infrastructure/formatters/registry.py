"""Resolves the correct :class:`~app.domain.ports.GreetingFormatter`."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.ports import GreetingFormatter


class FormatterRegistry:
    """Maps a locale to its formatter, falling back to a default.

    The registry is the *only* place that knows which formatters exist, so
    the service layer stays closed for modification.
    """

    def __init__(
        self, formatters: Iterable[GreetingFormatter], fallback: GreetingFormatter
    ) -> None:
        self._formatters: dict[str, GreetingFormatter] = {f.locale: f for f in formatters}
        self._fallback = fallback

    def register(self, formatter: GreetingFormatter) -> None:
        """Add or replace a formatter at runtime (used by plugins and tests)."""
        self._formatters[formatter.locale] = formatter

    def resolve(self, locale: str) -> GreetingFormatter:
        """Return the formatter for ``locale``, or the fallback."""
        return self._formatters.get(locale, self._fallback)
