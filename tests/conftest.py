import pytest
from app.main import app
from app.deps import get_db, _DummyDB

@pytest.fixture(autouse=True, scope="session")
def override_db_dependency():
    app.dependency_overrides[get_db] = lambda: _DummyDB()
    yield
    app.dependency_overrides.clear()
