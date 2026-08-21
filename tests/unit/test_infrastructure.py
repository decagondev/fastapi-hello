import pytest

from app.domain.models import Greeting, GreetingTemplate
from app.domain.ports import Clock, GreetingFormatter, GreetingTemplateRepository
from app.infrastructure.clock import FrozenClock, SystemClock
from app.infrastructure.formatters.base import DefaultFormatter
from app.infrastructure.formatters.japanese import JapaneseFormatter
from app.infrastructure.repositories.in_memory import InMemoryGreetingTemplateRepository
from tests.conftest import FROZEN_MOMENT

pytestmark = pytest.mark.unit


def test_adapters_satisfy_their_ports():
    assert isinstance(SystemClock(), Clock)
    assert isinstance(FrozenClock(FROZEN_MOMENT), Clock)
    assert isinstance(InMemoryGreetingTemplateRepository(), GreetingTemplateRepository)
    assert isinstance(DefaultFormatter(), GreetingFormatter)
    assert isinstance(JapaneseFormatter(), GreetingFormatter)


def test_system_clock_is_timezone_aware():
    assert SystemClock().now().tzinfo is not None


async def test_repository_returns_none_for_unknown_locale(templates):
    assert await templates.get("xx") is None


async def test_repository_locales_are_sorted(templates):
    locales = await templates.locales()
    assert list(locales) == sorted(locales)


def test_registry_falls_back_for_unknown_locale(formatters):
    assert isinstance(formatters.resolve("nope"), DefaultFormatter)


def test_template_renders_placeholder():
    template = GreetingTemplate(locale="en", pattern="Hi, {recipient}.")
    assert template.render("Ada") == "Hi, Ada."


def test_greeting_is_immutable():
    greeting = Greeting(recipient="Ada", message="Hi", locale="en", created_at=FROZEN_MOMENT)
    with pytest.raises((AttributeError, TypeError)):
        setattr(greeting, "recipient", "Grace")  # noqa: B010
