"""Structured logging configuration.

Emits either JSON (for log aggregation) or human-readable lines locally, and
attaches the current request id to every record.
"""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from typing import Any

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Injects the ambient request id onto each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Attach the ambient request id, then keep the record."""
        record.request_id = request_id_ctx.get()
        return True


class JsonFormatter(logging.Formatter):
    """Renders log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Return the record as a single-line JSON object."""
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(*, level: str = "INFO", json_output: bool = True) -> None:
    """Reset the root logger to this application's configuration."""
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        JsonFormatter()
        if json_output
        else logging.Formatter("%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s")
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    for noisy in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(noisy)
        logger.handlers.clear()
        logger.propagate = True
