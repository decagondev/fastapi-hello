"""Application service implementing the greeting use case.

Single Responsibility: this class orchestrates a greeting and nothing else.
It does not know how templates are stored, how time is read, or how the
result is serialised -- all of that arrives through injected ports.
"""

from __future__ import annotations

from app.domain.exceptions import InvalidRecipientError, UnsupportedLocaleError
from app.domain.models import Greeting
from app.domain.ports import Clock, FormatterResolver, GreetingTemplateRepository

MAX_RECIPIENT_LENGTH = 64


class GreetingService:
    """Builds a :class:`Greeting` for a recipient in a given locale."""

    def __init__(
        self,
        *,
        templates: GreetingTemplateRepository,
        formatters: FormatterResolver,
        clock: Clock,
        default_locale: str = "en",
    ) -> None:
        self._templates = templates
        self._formatters = formatters
        self._clock = clock
        self._default_locale = default_locale

    async def greet(self, recipient: str, locale: str | None = None) -> Greeting:
        """Return a greeting, raising a :class:`DomainError` if it cannot."""
        normalised_recipient = self._normalise_recipient(recipient)
        resolved_locale = (locale or self._default_locale).lower()

        template = await self._templates.get(resolved_locale)
        if template is None:
            raise UnsupportedLocaleError(resolved_locale, await self._templates.locales())

        formatter = self._formatters.resolve(resolved_locale)
        message = formatter.format(template, normalised_recipient)

        return Greeting(
            recipient=normalised_recipient,
            message=message,
            locale=resolved_locale,
            created_at=self._clock.now(),
        )

    async def supported_locales(self) -> tuple[str, ...]:
        """Return every locale that can currently be served."""
        return await self._templates.locales()

    @staticmethod
    def _normalise_recipient(recipient: str) -> str:
        cleaned = recipient.strip()
        if not cleaned:
            reason = "recipient must not be blank"
            raise InvalidRecipientError(reason)
        if len(cleaned) > MAX_RECIPIENT_LENGTH:
            reason = f"recipient must be at most {MAX_RECIPIENT_LENGTH} characters"
            raise InvalidRecipientError(reason)
        return cleaned
