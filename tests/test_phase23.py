import io, json, base64
import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def login(user):
    r = client.post("/auth/login", headers={"Host":"tenant1.lvh.me"}, json={"username":user,"password":"secret123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]

def auth(h, token): 
    h = {**h, "Authorization": f"Bearer {token}"}
    return h

def test_auth_bad_password():
    r = client.post("/auth/login", headers={"Host":"tenant1.lvh.me"}, json={"username":"owner","password":"wrong"})
    assert r.status_code in (400,401)

def test_tenant_mismatch_token():
    tok_t1 = login("owner")
    r = client.get("/admin/stats", headers=auth({"Host":"tenant2.lvh.me"}, tok_t1))
    assert r.status_code in (401,403)

def test_rbac_analyst_forbidden_on_admin():
    tok = login("analyst")
    r = client.get("/admin/stats", headers=auth({"Host":"tenant1.lvh.me"}, tok))
    assert r.status_code == 403

def test_rbac_owner_allows_admin():
    tok = login("owner")
    r = client.get("/admin/stats", headers=auth({"Host":"tenant1.lvh.me"}, tok))
    assert r.status_code == 200
    body = r.json()
    assert {"tenant","scan_count","qc_results","last_forecast"} <= set(body.keys())

def test_rudra_forecast_non_negative():
    tok = login("owner")
    r = client.post("/rudra/cloud/mock-usage", headers=auth({"Host":"tenant1.lvh.me"}, tok),
                    json={"usage":[20,25,30,33,31]})
    assert r.status_code == 200
    r = client.get("/rudra/cloud/forecast", headers=auth({"Host":"tenant1.lvh.me"}, tok))
    assert r.status_code == 200
    amt = r.json().get("amount_pred", 0)
    assert amt >= 0

def test_trinetra_upload_bytesio():
    tok = login("owner")
    fake_img = b"\xFF\xD8\xFF\xE0" + b"0"*256 + b"\xFF\xD9"  # tiny jpeg-ish blob
    files = {"image": ("tiny.jpg", io.BytesIO(fake_img), "image/jpeg")}
    r = client.post("/trinetra/qc/upload", headers=auth({"Host":"tenant1.lvh.me"}, tok), files=files)
    assert r.status_code == 200
    r2 = client.get("/trinetra/qc/results", headers=auth({"Host":"tenant1.lvh.me"}, tok))
    assert r2.status_code == 200
    assert isinstance(r2.json(), list) and len(r2.json()) >= 1

def test_rate_limit_dummy():
    # /dummy is limited to 5/min
    ok, too_many = 0, 0
    for _ in range(7):
        r = client.get("/dummy", headers={"Host":"tenant1.lvh.me"})
        if r.status_code == 200: ok += 1
        elif r.status_code == 429: too_many += 1
    assert ok == 5 and too_many >= 1
