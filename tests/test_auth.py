from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_round_trip():
    # signup (idempotent)
    r = client.post("/auth/signup",
                    headers={"Host":"tenant1.lvh.me"},
                    json={"username":"bhargav","password":"secret123","tenant":"tenant1"})
    assert r.status_code in (200, 400)

    # login
    r = client.post("/auth/login",
                    headers={"Host":"tenant1.lvh.me"},
                    json={"username":"bhargav","password":"secret123","tenant":"tenant1"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # protected
    r = client.get("/api/me",
                   headers={"Host":"tenant1.lvh.me","Authorization":f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["user"] == "bhargav"
    assert data["tenant"] == "tenant1"
