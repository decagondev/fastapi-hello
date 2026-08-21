"""Middleware assigning and propagating a request id."""

from __future__ import annotations

import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import request_id_ctx

REQUEST_ID_HEADER = b"x-request-id"


class RequestContextMiddleware:
    """Reads or generates ``X-Request-ID`` and echoes it on the response.

    Written as raw ASGI rather than ``BaseHTTPMiddleware`` so the context
    variable set here is visible to the endpoint and to streaming responses.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle one ASGI event stream."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        incoming = headers.get(REQUEST_ID_HEADER)
        request_id = incoming.decode() if incoming else uuid.uuid4().hex
        token = request_id_ctx.set(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].append((REQUEST_ID_HEADER, request_id.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            request_id_ctx.reset(token)
