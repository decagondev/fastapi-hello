import pytest

from app.domain.exceptions import InvalidRecipientError, UnsupportedLocaleError
from app.services.greeting_service import MAX_RECIPIENT_LENGTH
from tests.conftest import FROZEN_MOMENT

pytestmark = pytest.mark.unit


async def test_greets_in_default_locale(greeting_service):
    greeting = await greeting_service.greet("World")
    assert greeting.message == "Hello, World!"
    assert greeting.locale == "en"
    assert greeting.created_at == FROZEN_MOMENT


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en", "Hello, World!"),
        ("es", "¡Hola, World!"),
        ("fr", "Bonjour, World !"),
        ("de", "Hallo, World!"),
    ],
)
async def test_greets_in_each_locale(greeting_service, locale, expected):
    greeting = await greeting_service.greet("World", locale)
    assert greeting.message == expected


async def test_locale_is_case_insensitive(greeting_service):
    greeting = await greeting_service.greet("World", "EN")
    assert greeting.locale == "en"


async def test_japanese_formatter_adds_honorific(greeting_service):
    greeting = await greeting_service.greet("Yuki", "ja")
    assert greeting.message == "こんにちは、Yukiさん！"


async def test_japanese_formatter_is_idempotent(greeting_service):
    greeting = await greeting_service.greet("Yukiさん", "ja")
    assert greeting.message.count("さん") == 1


async def test_recipient_is_trimmed(greeting_service):
    greeting = await greeting_service.greet("  Ada  ")
    assert greeting.recipient == "Ada"


@pytest.mark.parametrize("recipient", ["", "   ", "\t"])
async def test_blank_recipient_rejected(greeting_service, recipient):
    with pytest.raises(InvalidRecipientError):
        await greeting_service.greet(recipient)


async def test_overlong_recipient_rejected(greeting_service):
    with pytest.raises(InvalidRecipientError, match="at most"):
        await greeting_service.greet("x" * (MAX_RECIPIENT_LENGTH + 1))


async def test_unknown_locale_rejected(greeting_service):
    with pytest.raises(UnsupportedLocaleError) as excinfo:
        await greeting_service.greet("World", "xx")
    assert "en" in excinfo.value.supported


async def test_supported_locales(greeting_service):
    assert await greeting_service.supported_locales() == ("de", "en", "es", "fr", "ja")
