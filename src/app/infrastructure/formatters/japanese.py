"""Japanese formatter -- an example of extending behaviour without editing it.

Adding this class required no change to ``GreetingService``: register it in
the composition root and the new locale is live (Open/Closed Principle).
"""

from __future__ import annotations

from app.domain.models import GreetingTemplate

_HONORIFIC = "さん"


class JapaneseFormatter:
    """Appends the ``さん`` honorific unless the recipient already has one."""

    @property
    def locale(self) -> str:
        """Return the locale this formatter handles."""
        return "ja"

    def format(self, template: GreetingTemplate, recipient: str) -> str:
        """Return the rendered greeting with the honorific applied."""
        polite = recipient if recipient.endswith(_HONORIFIC) else f"{recipient}{_HONORIFIC}"
        return template.render(polite)
