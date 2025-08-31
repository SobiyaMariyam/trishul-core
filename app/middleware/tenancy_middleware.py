from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import os

from app.auth.jwt import decode_token

def _extract_tenant_from_host(host: str, local_domain: str) -> Optional[str]:
    """
    For dev we use subdomains like: tenant1.lvh.me
    If host is 'tenant1.lvh.me:8000', strip port and return 'tenant1'.
    """
    if not host:
        return None
    host = host.split(":")[0].strip().lower()
    # if exact domain (lvh.me) -> no tenant
    if host == local_domain:
        return None
    # expecting "<tenant>.<local_domain>"
    suffix = f".{local_domain}"
    if host.endswith(suffix):
        return host[: -len(suffix)]
    return None

class TenancyMiddleware(BaseHTTPMiddleware):
    """
    - Resolves tenant from Host header (e.g., tenant1.lvh.me)
    - If Authorization: Bearer <jwt> present, decodes and attaches claims to request.state
    - Validates that token 'tid' matches resolved tenant (if both present)
    """

    def __init__(self, app):
        super().__init__(app)
        self.local_domain = os.getenv("LOCAL_DOMAIN", "lvh.me").lower()

    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        tenant = _extract_tenant_from_host(host, self.local_domain)
        request.state.tenant = tenant  # may be None for public routes

        # Default: no claims
        request.state.claims = None

        # Try decode JWT if provided
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            try:
                claims = decode_token(token)
                request.state.claims = claims
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"invalid token: {exc}",
                )

        # If both tenant and claims.tid exist, enforce match
        if tenant and request.state.claims:
            tid = str(request.state.claims.get("tid", "")).lower()
            if tid != tenant.lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token tenant mismatch",
                )

        response = await call_next(request)
        return response
