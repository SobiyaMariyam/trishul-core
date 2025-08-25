from fastapi.testclient import TestClient
from app import main


def test_health_endpoint():
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("ok") is True
