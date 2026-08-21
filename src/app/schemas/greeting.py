"""Pydantic contracts for the greetings API.

Schemas live at the edge of the system: they describe the wire format only.
Domain objects are converted here so that changing the public API never
forces a change to the domain, and vice versa.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import Greeting

RecipientField = Annotated[
    str,
    Field(min_length=1, max_length=64, description="Who to greet.", examples=["World"]),
]
LocaleField = Annotated[
    str,
    Field(
        min_length=2,
        max_length=8,
        pattern=r"^[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?$",
        description="BCP-47 style language tag.",
        examples=["en"],
    ),
]


class GreetingRequest(BaseModel):
    """Body accepted by ``POST /greetings``."""

    model_config = ConfigDict(extra="forbid")

    recipient: RecipientField = "World"
    locale: LocaleField | None = None


class GreetingResponse(BaseModel):
    """A rendered greeting."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recipient": "World",
                "message": "Hello, World!",
                "locale": "en",
                "created_at": "2026-01-01T12:00:00Z",
            }
        }
    )

    recipient: str
    message: str
    locale: str
    created_at: datetime

    @classmethod
    def from_domain(cls, greeting: Greeting) -> Self:
        """Build the response DTO from a domain entity."""
        return cls(
            recipient=greeting.recipient,
            message=greeting.message,
            locale=greeting.locale,
            created_at=greeting.created_at,
        )


class LocalesResponse(BaseModel):
    """Every locale the service can render."""

    locales: list[str]
    default: str
