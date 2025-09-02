import os
import re

from fastapi import HTTPException, Request

from app.db.manager import get_core_db, get_tenant_db

TENANT_HEADER = "x-tenant"
LOCAL_DOMAIN = os.getenv("LOCAL_DOMAIN", "lvh.me")


async def tenancy_middleware(request: Request, call_next):
    host = request.headers.get("host", "")
    tenant = request.headers.get(TENANT_HEADER)

    if not tenant:
        pattern = rf"^([a-z0-9-]+)\.{re.escape(LOCAL_DOMAIN)}"
        m = re.match(pattern, host, flags=re.I)
        tenant = m.group(1) if m else None

    open_paths = ["/", "/health", "/signup", "/admin"]
    if tenant is None and request.url.path in open_paths:
        return await call_next(request)

    if tenant is None:
        raise HTTPException(status_code=400, detail="Tenant not provided")

    core = get_core_db()
    found = core.tenants.find_one({"slug": tenant, "status": "active"})
    if not found:
        raise HTTPException(status_code=404, detail="Unknown tenant")

    request.state.tenant = tenant
    request.state.tenant_db = get_tenant_db(tenant)

    return await call_next(request)
