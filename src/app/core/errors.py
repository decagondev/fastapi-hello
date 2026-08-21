"""Translates domain errors into RFC 9457 style HTTP problem responses.

Keeping this mapping in one module means the domain never imports FastAPI and
the endpoints never repeat try/except blocks.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import request_id_ctx
from app.domain.exceptions import DomainError, InvalidRecipientError, UnsupportedLocaleError

logger = logging.getLogger(__name__)

Handler = Callable[[Request, Exception], Awaitable[JSONResponse]]

# Plain ``http.HTTPStatus`` values keep this table framework-agnostic and
# immune to Starlette renaming its status constants between versions.
UNPROCESSABLE = int(HTTPStatus.UNPROCESSABLE_ENTITY)
BAD_REQUEST = int(HTTPStatus.BAD_REQUEST)
INTERNAL_ERROR = int(HTTPStatus.INTERNAL_SERVER_ERROR)

_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    UnsupportedLocaleError: UNPROCESSABLE,
    InvalidRecipientError: UNPROCESSABLE,
}


def problem_response(
    *, status_code: int, code: str, detail: str, extra: dict[str, object] | None = None
) -> JSONResponse:
    """Build a consistent error body used by every failure path."""
    body: dict[str, object] = {
        "type": f"https://httpstatuses.io/{status_code}",
        "title": HTTPStatus(status_code).phrase,
        "status": status_code,
        "code": code,
        "detail": detail,
        "request_id": request_id_ctx.get(),
    }
    if extra:
        body.update(extra)
    return JSONResponse(status_code=status_code, content=body)


async def domain_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Map a :class:`DomainError` onto the appropriate HTTP status."""
    assert isinstance(exc, DomainError)  # noqa: S101 - narrowed by registration
    status_code = _STATUS_BY_ERROR.get(type(exc), BAD_REQUEST)
    extra: dict[str, object] | None = None
    if isinstance(exc, UnsupportedLocaleError):
        extra = {"supported_locales": list(exc.supported)}
    return problem_response(status_code=status_code, code=exc.code, detail=str(exc), extra=extra)


async def validation_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Render FastAPI validation failures in the shared problem format."""
    assert isinstance(exc, RequestValidationError)  # noqa: S101
    return problem_response(
        status_code=UNPROCESSABLE,
        code="validation_error",
        detail="Request validation failed.",
        extra={"errors": exc.errors()},
    )


async def unhandled_error_handler(request: Request, _exc: Exception) -> JSONResponse:
    """Log and mask any error we did not anticipate."""
    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return problem_response(
        status_code=INTERNAL_ERROR,
        code="internal_error",
        detail="An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach every handler to the application."""
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
