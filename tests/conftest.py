import pytest
import os

# Set required environment variables for tests
os.environ["CORE_DB"] = "test_core_db"
os.environ["MONGO_URI"] = "mongodb://test:test@localhost:27017/test"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["LOCAL_DOMAIN"] = "lvh.me"


@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    """Patch DB calls so tests don't need a real Mongo instance."""
    
    # Store users in memory for the test session
    test_users = {}
    
    # Pre-populate with test users
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Add the test user that the auth test expects
    test_user = {
        "username": "analyst",
        "password": pwd_context.hash("secret123"),
        "tenant": "tenant1",
        "role": "analyst"
    }
    test_users["analyst_tenant1"] = test_user

    def fake_core_db():
        class DummyCore:
            def __init__(self):
                class Tenants:
                    def find_one(self, query):
                        # Handle tenant lookup based on slug
                        if query and "slug" in query:
                            slug = query["slug"]
                            if slug in ["test", "tenant1"]:
                                return {"slug": slug, "status": "active"}
                        return {"slug": "tenant1", "status": "active"}

                class Users:
                    def find_one(self, query):
                        # Create a key from username and tenant
                        username = query.get("username")
                        tenant = query.get("tenant")
                        if username and tenant:
                            key = f"{username}_{tenant}"
                            return test_users.get(key)
                        return None
                    
                    def insert_one(self, document):
                        # Store the user for later retrieval
                        username = document.get("username")
                        tenant = document.get("tenant")
                        if username and tenant:
                            key = f"{username}_{tenant}"
                            test_users[key] = document
                        return {"inserted_id": "dummy_id"}

                self.tenants = Tenants()
                self.users = Users()

        return DummyCore()

    def fake_tenant_db(_slug: str):
        class DummyTenant:
            pass

        return DummyTenant()

    # Patch database functions at their source
    monkeypatch.setattr("app.db.manager.get_core_db", fake_core_db)
    monkeypatch.setattr("app.db.manager.get_tenant_db", fake_tenant_db)
    monkeypatch.setattr("app.middleware.tenancy.get_core_db", fake_core_db)
    monkeypatch.setattr("app.middleware.tenancy.get_tenant_db", fake_tenant_db)
