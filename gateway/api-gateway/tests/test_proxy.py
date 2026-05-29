import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "api-gateway"
    assert "docs" in data


def test_proxy_open_route_no_auth(client):
    response = client.post("/api/v1/login", json={
        "username": "test@example.com",
        "password": "TestPass1!"
    })
    assert response.status_code in (200, 401, 502)


def test_proxy_protected_route_without_auth(client):
    response = client.get("/api/v1/me")
    assert response.status_code == 401


def test_proxy_unknown_path(client):
    response = client.get("/api/v2/unknown")
    assert response.status_code == 404
    assert "No backend" in response.json()["detail"]


def test_docs_accessible(client):
    response = client.get("/docs")
    assert response.status_code == 200
    response = client.get("/openapi.json")
    assert response.status_code == 200
