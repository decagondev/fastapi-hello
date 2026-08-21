import json
import logging
import sys

import pytest

from app.core.config import Settings
from app.core.container import build_container
from app.core.logging import JsonFormatter, RequestIdFilter, configure_logging, request_id_ctx
from app.services.greeting_service import GreetingService

pytestmark = pytest.mark.unit


def _record(message: str = "hello") -> logging.LogRecord:
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )


def test_json_formatter_emits_valid_json():
    record = _record()
    RequestIdFilter().filter(record)
    payload = json.loads(JsonFormatter().format(record))
    assert payload["message"] == "hello"
    assert payload["level"] == "INFO"
    assert payload["request_id"] == "-"


def test_json_formatter_includes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        record = _record("failed")
        record.exc_info = sys.exc_info()
    payload = json.loads(JsonFormatter().format(record))
    assert "ValueError" in payload["exception"]


def test_request_id_filter_reads_context():
    token = request_id_ctx.set("req-42")
    try:
        record = _record()
        RequestIdFilter().filter(record)
        assert record.request_id == "req-42"  # type: ignore[attr-defined]
    finally:
        request_id_ctx.reset(token)


@pytest.mark.parametrize("json_output", [True, False])
def test_configure_logging_installs_single_handler(json_output):
    configure_logging(level="DEBUG", json_output=json_output)
    root = logging.getLogger()
    assert len(root.handlers) == 1
    assert root.level == logging.DEBUG
    configure_logging(level="WARNING", json_output=False)


def test_is_production_flag():
    assert Settings(environment="production").is_production is True
    assert Settings(environment="local").is_production is False


def test_container_wires_the_object_graph():
    settings = Settings(environment="test", default_locale="fr")
    container = build_container(settings)
    assert isinstance(container.greeting_service, GreetingService)
    assert container.settings is settings
    assert container.formatters.resolve("ja").locale == "ja"


async def test_container_uses_configured_default_locale():
    container = build_container(Settings(environment="test", default_locale="de"))
    greeting = await container.greeting_service.greet("Welt")
    assert greeting.message == "Hallo, Welt!"
