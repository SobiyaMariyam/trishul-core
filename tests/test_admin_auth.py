import time, jwt
SECRET = "dev-secret-key"

def mint(sub, tid, role, ttl=300):
    now = int(time.time())
    return jwt.encode(
        {"sub": sub, "tid": tid, "role": role, "iat": now, "exp": now+ttl},
        SECRET, algorithm="HS256"
    )

def test_me_owner(httpx_client):
    tok = mint("employee@tenant1.com", "tenant1", "owner")
    r = httpx_client.get("/api/me", headers={
        "Host": "tenant1.lvh.me", "Authorization": f"Bearer {tok}"
    })
    assert r.status_code == 200
    assert r.json()["tenant"] == "tenant1"

def test_admin_analyst_forbidden(httpx_client):
    tok = mint("employee@tenant1.com", "tenant1", "analyst")
    r = httpx_client.get("/admin/health", headers={
        "Host": "tenant1.lvh.me", "Authorization": f"Bearer {tok}"
    })
    assert r.status_code == 403

def test_admin_tenant_mismatch_unauthorized(httpx_client):
    tok = mint("employee@tenant1.com", "tenant2", "owner")
    r = httpx_client.get("/admin/health", headers={
        "Host": "tenant1.lvh.me", "Authorization": f"Bearer {tok}"
    })
    assert r.status_code == 401
