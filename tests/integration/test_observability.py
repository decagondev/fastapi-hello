import pytest

pytestmark = pytest.mark.integration


async def test_health_endpoints(client):
    for path in ("/api/v1/health/live", "/api/v1/health/ready"):
        response = await client.get(path)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


async def test_request_id_is_generated(client):
    response = await client.get("/api/v1/health/live")
    assert response.headers["x-request-id"]


async def test_request_id_is_echoed_when_supplied(client):
    response = await client.get("/api/v1/health/live", headers={"X-Request-ID": "abc-123"})
    assert response.headers["x-request-id"] == "abc-123"


async def test_process_time_header_present(client):
    response = await client.get("/api/v1/health/live")
    assert float(response.headers["x-process-time-ms"]) >= 0


async def test_openapi_schema_is_served(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/greetings/hello" in response.json()["paths"]
