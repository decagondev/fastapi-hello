"""Domain-level exceptions.

The domain raises these; the API layer is responsible for translating them
into HTTP responses. The domain therefore never imports ``fastapi``.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for every error raised by the domain layer."""

    code: str = "domain_error"


class UnsupportedLocaleError(DomainError):
    """Raised when a greeting is requested in a locale we cannot serve."""

    code = "unsupported_locale"

    def __init__(self, locale: str, supported: tuple[str, ...]) -> None:
        self.locale = locale
        self.supported = supported
        super().__init__(
            f"Locale {locale!r} is not supported. Supported locales: {', '.join(supported)}."
        )


class InvalidRecipientError(DomainError):
    """Raised when the recipient name fails domain validation."""

    code = "invalid_recipient"

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid recipient: {reason}")
