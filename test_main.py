from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_stats_anonymous():
    response = client.get("/stats")
    assert response.status_code == 403
