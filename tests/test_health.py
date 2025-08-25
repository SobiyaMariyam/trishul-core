import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    def fake_core_db():
        class DummyCore:
            def __init__(self):
                class Tenants:
                    def find_one(self, _query):
                        return {"slug": "test", "status": "active"}

                self.tenants = Tenants()

        return DummyCore()

    def fake_tenant_db(_slug):
        class DummyTenant:
            pass

        return DummyTenant()

    monkeypatch.setattr("app.middleware.tenancy.get_core_db", fake_core_db)
    monkeypatch.setattr("app.middleware.tenancy.get_tenant_db", fake_tenant_db)


def test_health():
    client = TestClient(main.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True
