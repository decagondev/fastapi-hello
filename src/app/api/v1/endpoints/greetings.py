"""Greeting endpoints.

These functions are thin: parse input, call the use case, serialise output.
All business rules live in ``app.services``; all error mapping lives in
``app.core.errors``.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import GreetingServiceDep, SettingsDep
from app.schemas.greeting import GreetingRequest, GreetingResponse, LocalesResponse

router = APIRouter(prefix="/greetings", tags=["greetings"])


@router.get(
    "/hello",
    response_model=GreetingResponse,
    summary="Say hello",
    responses={422: {"description": "Unsupported locale or invalid recipient"}},
)
async def say_hello(
    service: GreetingServiceDep,
    name: Annotated[str, Query(min_length=1, max_length=64)] = "World",
    locale: Annotated[str | None, Query(min_length=2, max_length=8)] = None,
) -> GreetingResponse:
    """Return a greeting for ``name``, optionally in a specific ``locale``."""
    greeting = await service.greet(name, locale)
    return GreetingResponse.from_domain(greeting)


@router.post(
    "",
    response_model=GreetingResponse,
    status_code=200,
    summary="Say hello (structured request)",
)
async def create_greeting(
    payload: GreetingRequest, service: GreetingServiceDep
) -> GreetingResponse:
    """Return a greeting built from a JSON request body."""
    greeting = await service.greet(payload.recipient, payload.locale)
    return GreetingResponse.from_domain(greeting)


@router.get("/locales", response_model=LocalesResponse, summary="List supported locales")
async def list_locales(service: GreetingServiceDep, settings: SettingsDep) -> LocalesResponse:
    """Return every locale the service can render, plus the default."""
    locales = await service.supported_locales()
    return LocalesResponse(locales=list(locales), default=settings.default_locale)
