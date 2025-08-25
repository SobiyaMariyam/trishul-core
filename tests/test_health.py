from fastapi.testclient import TestClient
import pytest

from app import main


@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    # dummy core db
    def fake_core_db():
        class Dummy:
            tenants = {"find_one": lambda self, q: {"slug": "test", "status": "active"}}
        return Dummy()

    # dummy tenant db
    def fake_tenant_db(slug):
        return {}

    monkeypatch.setattr("app.middleware.tenancy.get_core_db", fake_core_db)
    monkeypatch.setattr("app.middleware.tenancy.get_tenant_db", fake_tenant_db)


def test_health():
    client = TestClient(main.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True
