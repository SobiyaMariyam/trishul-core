from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import HTTPException
from jose import jwt, JWTError

from app.core.config import settings


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise Exception(f"invalid token: {exc}")


def _extract_tenant_from_host(host: str, local_domain: str) -> str | None:
    if not host:
        return None
    host = host.lower()
    # If host ends with our local dev domain (e.g., lvh.me), use the subdomain as tenant.
    if host.endswith(local_domain):
        sub = host.replace(f".{local_domain}", "")
        # Handle cases like "tenant1.lvh.me" (sub="tenant1") vs "lvh.me" (no tenant)
        if sub and sub != local_domain:
            return sub.split(".")[0]
    # For other environments you might parse differently; for tests we only need the above.
    return None


class TenancyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, local_domain: str = "lvh.me"):
        super().__init__(app)
        self.local_domain = local_domain

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
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": f"invalid token: {exc}"},
                )

        # Enforce tenant match ONLY if token actually has a non-empty 'tid' claim.
        if tenant and request.state.claims:
            tid = str(request.state.claims.get("tid", "") or "").strip().lower()
            if tid:  # only enforce when present
                if tid != tenant.lower():
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "token tenant mismatch"},
                    )

        return await call_next(request)
