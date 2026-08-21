"""Domain entities.

These are pure Python objects. They know nothing about FastAPI, Pydantic,
HTTP, or any storage mechanism -- that isolation is what keeps the domain
testable and lets the outer layers change without touching business rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class GreetingTemplate:
    """A locale-specific template used to render a greeting."""

    locale: str
    pattern: str
    """A format string containing a single ``{recipient}`` placeholder."""

    def render(self, recipient: str) -> str:
        """Interpolate ``recipient`` into the pattern."""
        return self.pattern.format(recipient=recipient)


@dataclass(frozen=True, slots=True)
class Greeting:
    """The result of greeting someone: the core output of this service."""

    recipient: str
    message: str
    locale: str
    created_at: datetime
