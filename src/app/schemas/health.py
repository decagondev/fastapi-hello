"""Pydantic contracts for health and metadata endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness / readiness payload."""

    status: Literal["ok", "degraded"]
    service: str
    version: str
    environment: str


class ServiceInfoResponse(BaseModel):
    """Root endpoint payload pointing clients at the API."""

    service: str
    version: str
    docs_url: str | None
    api_prefix: str
