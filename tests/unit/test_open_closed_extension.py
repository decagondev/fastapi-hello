"""Proof that a new locale can be added without touching existing code."""

import pytest

from app.domain.models import GreetingTemplate
from app.infrastructure.repositories.in_memory import InMemoryGreetingTemplateRepository
from app.services.greeting_service import GreetingService

pytestmark = pytest.mark.unit


class ShoutingFormatter:
    """A third-party formatter, defined entirely outside the application."""

    @property
    def locale(self) -> str:
        return "en-shout"

    def format(self, template: GreetingTemplate, recipient: str) -> str:
        return template.render(recipient).upper()


async def test_new_formatter_plugs_in_without_modifying_the_service(formatters, clock):
    formatters.register(ShoutingFormatter())
    service = GreetingService(
        templates=InMemoryGreetingTemplateRepository({"en-shout": "Hello, {recipient}!"}),
        formatters=formatters,
        clock=clock,
    )

    greeting = await service.greet("World", "en-shout")

    assert greeting.message == "HELLO, WORLD!"
