import re
from fastapi import APIRouter, Depends, Header, HTTPException
from app.auth.deps import get_current_claims

router = APIRouter(prefix="/api", tags=["protected"])

def _extract_tenant_from_import re
from fastapi import APIRouter, Depends, Header, HTTPException

router = APIRouter(prefix="/api", tags=["protected"])

def _extract_tenant_from_host(host: str, local_domain: str = "lvh.me") -> str:
    # Accept both 'tenant.lvh.me' and 'tenant.lvh.me:8000'
    m = re.match(
        rf"^([a-z0-9-]+)\.{re.escape(local_domain)}(:\d+)?$",
        host or "",
        flags=re.I
    )
    return m.group(1) if m else ""

@router.get("/me")
def me(
    claims: dict = Depends(get_current_claims),
    host: str = Header(default="", alias="host"),
):
    token_tenant = claims.get("tenant") or ""
    host_tenant = _extract_tenant_from_host(host)
    if not host_tenant:
        raise HTTPException(status_code=400, detail="Missing or invalid Host header")
    if token_tenant.lower() != host_tenant.lower():
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    return {"user": claims.get("sub"), "tenant": token_tenant}
host(host: str, local_domain: str = "lvh.me") -> str:
    # Accept both 'tenant.lvh.me' and 'tenant.lvh.me:8000'
    m = re.match(rf"^([a-z0-9-]+)\.{re.escape(local_domain)}(:\d+)?$", host or "", flags=re.I)
    return m.group(1) if m else ""

@router.get("/me")
def me(
    claims: dict = Depends(get_current_claims),
    host: str = Header(default="", alias="host"),
):
    token_tenant = claims.get("tenant") or ""
    host_tenant = _extract_tenant_from_host(host)
    if not host_tenant:
        raise HTTPException(status_code=400, detail="Missing or invalid Host header")
    if token_tenant.lower() != host_tenant.lower():
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    return {"user": claims.get("sub"), "tenant": token_tenant}
