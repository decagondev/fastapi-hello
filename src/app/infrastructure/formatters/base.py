"""The default greeting formatter."""

from __future__ import annotations

from app.domain.models import GreetingTemplate


class DefaultFormatter:
    """Renders the template verbatim with the recipient interpolated.

    Every other formatter is substitutable for this one (Liskov): same
    signature, same return type, no extra preconditions.
    """

    def __init__(self, locale: str = "en") -> None:
        self._locale = locale

    @property
    def locale(self) -> str:
        """Return the locale this formatter handles."""
        return self._locale

    def format(self, template: GreetingTemplate, recipient: str) -> str:
        """Return the rendered greeting."""
        return template.render(recipient)
