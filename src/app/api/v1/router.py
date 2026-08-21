"""Aggregates every v1 endpoint router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import greetings, health

api_router_v1 = APIRouter()
api_router_v1.include_router(health.router)
api_router_v1.include_router(greetings.router)
