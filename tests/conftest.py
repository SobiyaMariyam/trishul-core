import pytest
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def httpx_client():
    with TestClient(app) as c:
        yield c
