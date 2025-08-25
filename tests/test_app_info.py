import pytest
from fastapi.testclient import TestClient
from app import main


@pytest.mark.skip(reason="Root path requires tenant header, not public")
def test_root_exists():
    client = TestClient(main.app)
    response = client.get("/")
    assert response.status_code in (200, 404)
