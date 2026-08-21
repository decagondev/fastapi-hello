"""Middleware recording how long each request took."""

from __future__ import annotations

import logging
import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)

PROCESS_TIME_HEADER = b"x-process-time-ms"


class TimingMiddleware:
    """Adds an ``X-Process-Time-Ms`` header and logs request duration."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle one ASGI event stream."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = time.perf_counter()
        status_code = 500

        async def send_with_timing(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                elapsed_ms = (time.perf_counter() - started) * 1000
                message.setdefault("headers", [])
                message["headers"].append((PROCESS_TIME_HEADER, f"{elapsed_ms:.2f}".encode()))
            await send(message)

        await self.app(scope, receive, send_with_timing)
        logger.info(
            "%s %s -> %s in %.2fms",
            scope.get("method"),
            scope.get("path"),
            status_code,
            (time.perf_counter() - started) * 1000,
        )
