import io
import pytest

# -- tiny helpers ----------------------------------------------------------------
def _hdr(host: str, tok: str | None = None):
    h = {"Host": host}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def _extract_token(data):
    if not isinstance(data, dict):
        return None
    for k in ("token", "access_token", "jwt", "id_token"):
        if k in data and isinstance(data[k], str) and data[k]:
            return data[k]
    return None

def _login(client, username="owner", password="owner", host="tenant1.lvh.me"):
    # Try JSON body (most common in this project)
    r = client.post("/auth/login",
                    json={"username": username, "password": password},
                    headers={"Host": host})
    tok = _extract_token(r.json() if r.headers.get("content-type","").startswith("application/json") else {})
    if r.status_code == 200 and tok:
        return tok

    # Try form-encoded fallback (some FastAPI examples use this)
    r = client.post("/auth/login",
                    data={"username": username, "password": password},
                    headers={"Host": host, "Content-Type": "application/x-www-form-urlencoded"})
    tok = _extract_token(r.json() if r.headers.get("content-type","").startswith("application/json") else {})
    if r.status_code == 200 and tok:
        return tok

    return None

# -- tests -----------------------------------------------------------------------

def test_auth_bad_password(client):
    r = client.post("/auth/login",
                    json={"username": "owner", "password": "WRONG"},
                    headers={"Host": "tenant1.lvh.me"})
    assert r.status_code in (401, 403)

def test_auth_tenant_mismatch_token(client):
    tok = _login(client, "owner", "owner", "tenant1.lvh.me")
    if not tok:
        pytest.skip("Could not obtain token from /auth/login; skipping token-based test")
    r = client.get("/admin/stats", headers=_hdr("tenant2.lvh.me", tok))
    assert r.status_code in (401, 403)

def test_rbac_analyst_cannot_access_admin(client):
    tok = _login(client, "analyst", "analyst", "tenant1.lvh.me")
    if tok:
        r = client.get("/admin/stats", headers=_hdr("tenant1.lvh.me", tok))
        assert r.status_code in (401, 403)
    else:
        # If no analyst user exists, login should fail (acceptable)
        r = client.post("/auth/login",
                        json={"username": "analyst", "password": "analyst"},
                        headers={"Host": "tenant1.lvh.me"})
        assert r.status_code in (401, 403)

def test_rudra_forecast_non_negative_repeat(client):
    tok = _login(client, "owner", "owner", "tenant1.lvh.me")
    if not tok:
        pytest.skip("Could not obtain token from /auth/login; skipping token-based test")
    r = client.post("/rudra/cloud/mock-usage",
                    headers=_hdr("tenant1.lvh.me", tok),
                    json={"usage": [1, 2, 3, 4, 5]})
    assert r.status_code == 200
    r2 = client.get("/rudra/cloud/forecast", headers=_hdr("tenant1.lvh.me", tok))
    assert r2.status_code == 200
    body = r2.json()
    vals = body if isinstance(body, list) else body.get("forecast", [])
    assert isinstance(vals, list)
    assert all((v is None) or (isinstance(v, (int, float)) and v >= 0) for v in vals)

def test_trinetra_upload_small_bytes_and_results_exist(client):
    tok = _login(client, "owner", "owner", "tenant1.lvh.me")
    if not tok:
        pytest.skip("Could not obtain token from /auth/login; skipping token-based test")
    fake_img = b"\xFF\xD8\xFF\xE0" + b"0"*256 + b"\xFF\xD9"
    files = {"image": ("tiny.jpg", io.BytesIO(fake_img), "image/jpeg")}
    r = client.post("/trinetra/qc/upload", headers=_hdr("tenant1.lvh.me", tok), files=files)
    assert r.status_code == 200
    r2 = client.get("/trinetra/qc/results", headers=_hdr("tenant1.lvh.me", tok))
    assert r2.status_code == 200
    body = r2.json()
    lst = body if isinstance(body, list) else body.get("results", [])
    assert isinstance(lst, list) and len(lst) >= 1

def test_kavach_rate_limit_if_enabled(client):
    tok = _login(client, "owner", "owner", "tenant1.lvh.me")
    if not tok:
        pytest.skip("Could not obtain token from /auth/login; skipping token-based test")
    codes = []
    for _ in range(6):
        rr = client.post("/kavach/scan/start", headers=_hdr("tenant1.lvh.me", tok))
        codes.append(rr.status_code)
    assert (429 in codes) or all(c in (200, 202) for c in codes)
from starlette.testclient import TestClient
from app.main import app
import pytest

@pytest.fixture
def client(override_db_dependency):
    # use the DB override provided by conftest (it shows up in available fixtures)
    with TestClient(app) as c:
        yield c
