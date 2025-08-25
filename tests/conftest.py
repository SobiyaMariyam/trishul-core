import pytest


@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    """Patch DB calls so tests don't need a real Mongo instance."""

    def fake_core_db():
        class DummyCore:
            def __init__(self):
                class Tenants:
                    def find_one(self, _query):
                        return {"slug": "test", "status": "active"}

                self.tenants = Tenants()

        return DummyCore()

    def fake_tenant_db(_slug: str):
        class DummyTenant:
            pass

        return DummyTenant()

    monkeypatch.setattr("app.middleware.tenancy.get_core_db", fake_core_db)
    monkeypatch.setattr("app.middleware.tenancy.get_tenant_db", fake_tenant_db)
