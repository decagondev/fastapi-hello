import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app

pytestmark = pytest.mark.integration


async def _client_for(app: FastAPI) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_docs_can_be_disabled(container):
    settings = Settings(environment="production", docs_enabled=False, log_json=False)
    app = create_app(settings=settings, container=container)
    async with await _client_for(app) as client:
        assert (await client.get("/docs")).status_code == 404
        assert (await client.get("/openapi.json")).status_code == 404
        assert (await client.get("/")).json()["docs_url"] is None


async def test_cors_headers_when_origins_configured(container):
    settings = Settings(environment="test", log_json=False, cors_origins=("https://example.com",))
    app = create_app(settings=settings, container=container)
    async with await _client_for(app) as client:
        response = await client.get("/", headers={"Origin": "https://example.com"})
    assert response.headers["access-control-allow-origin"] == "https://example.com"


async def test_unhandled_errors_return_a_masked_problem_document(app):
    async def boom() -> None:
        raise RuntimeError("internal detail that must not leak")

    app.add_api_route("/boom", boom, methods=["GET"], include_in_schema=False)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "internal_error"
    assert "internal detail" not in response.text


async def test_lifespan_runs_startup_and_shutdown(app):
    transport = ASGITransport(app=app)
    async with (
        AsyncClient(transport=transport, base_url="http://testserver") as client,
        app.router.lifespan_context(app),
    ):
        assert (await client.get("/api/v1/health/live")).status_code == 200
