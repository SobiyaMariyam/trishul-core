from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_round_trip():
    # Skip signup since we're using hardcoded users
    # Test login with existing hardcoded user
    r = client.post("/auth/login",
                    headers={"Host":"tenant1.lvh.me"},
                    json={"username":"analyst","password":"secret123"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # protected
    r = client.get("/api/me",
                   headers={"Host":"tenant1.lvh.me","Authorization":f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["user"] == "analyst"
    assert data["tenant"] == "tenant1"
