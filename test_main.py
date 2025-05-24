from fastapi.testclient import TestClient
from main import app, parse_token


def test_get_stats_anonymous():
    client = TestClient(app)
    response = client.get("/stats")
    assert response.status_code == 403


def test_get_stats_with_token():
    app.dependency_overrides[parse_token] = lambda: "ok"
    client = TestClient(app)
    response = client.get("/stats", headers={"Token": "token"})
    assert response.status_code == 200
    app.dependency_overrides.clear()


def test_get_stats_with_invalid_token():
    app.dependency_overrides[parse_token] = lambda: None
    client = TestClient(app)
    response = client.get("/stats", headers={"Token": "token"})
    assert response.status_code == 403
    app.dependency_overrides.clear()
