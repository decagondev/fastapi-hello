"""In-memory implementation of :class:`GreetingTemplateRepository`.

Swapping this for a SQL or Redis adapter means writing one new class and
changing one line in the composition root -- no service or API code moves.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.domain.models import GreetingTemplate

DEFAULT_TEMPLATES: Mapping[str, str] = {
    "en": "Hello, {recipient}!",
    "es": "¡Hola, {recipient}!",
    "fr": "Bonjour, {recipient} !",
    "de": "Hallo, {recipient}!",
    "ja": "こんにちは、{recipient}！",
}


class InMemoryGreetingTemplateRepository:
    """Serves templates from a dictionary held in process memory."""

    def __init__(self, templates: Mapping[str, str] | None = None) -> None:
        source = DEFAULT_TEMPLATES if templates is None else templates
        self._templates: dict[str, GreetingTemplate] = {
            locale: GreetingTemplate(locale=locale, pattern=pattern)
            for locale, pattern in source.items()
        }

    async def get(self, locale: str) -> GreetingTemplate | None:
        """Return the template for ``locale``, or ``None`` if unknown."""
        return self._templates.get(locale)

    async def locales(self) -> tuple[str, ...]:
        """Return every available locale, sorted."""
        return tuple(sorted(self._templates))
