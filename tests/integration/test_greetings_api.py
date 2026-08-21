import pytest

pytestmark = pytest.mark.integration


async def test_root_returns_service_info(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["api_prefix"] == "/api/v1"


async def test_hello_defaults_to_world(client):
    response = await client.get("/api/v1/greetings/hello")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Hello, World!"
    assert body["locale"] == "en"


async def test_hello_with_name_and_locale(client):
    response = await client.get("/api/v1/greetings/hello", params={"name": "Ada", "locale": "fr"})
    assert response.status_code == 200
    assert response.json()["message"] == "Bonjour, Ada !"


async def test_post_greeting(client):
    response = await client.post("/api/v1/greetings", json={"recipient": "Ada", "locale": "de"})
    assert response.status_code == 200
    assert response.json()["message"] == "Hallo, Ada!"


async def test_post_greeting_rejects_unknown_fields(client):
    response = await client.post("/api/v1/greetings", json={"recipient": "Ada", "nope": 1})
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


async def test_unsupported_locale_returns_problem_document(client):
    response = await client.get("/api/v1/greetings/hello", params={"name": "Ada", "locale": "zz"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "unsupported_locale"
    assert "en" in body["supported_locales"]
    assert body["request_id"]


async def test_blank_name_is_rejected_by_the_schema(client):
    response = await client.get("/api/v1/greetings/hello", params={"name": ""})
    assert response.status_code == 422


async def test_locales_endpoint(client):
    response = await client.get("/api/v1/greetings/locales")
    assert response.status_code == 200
    body = response.json()
    assert body["default"] == "en"
    assert "ja" in body["locales"]
