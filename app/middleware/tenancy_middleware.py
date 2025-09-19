from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

from app.core.config import settings
from app.auth.rbac import ensure_role


def decode_token(token: str, expected_aud: str | None = None):
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=expected_aud if expected_aud else None,
            options={"verify_aud": expected_aud is not None}
        )
    except JWTError as exc:
        raise Exception(f"invalid token: {exc}")


def _extract_tenant_from_host(host: str, local_domain: str) -> str | None:
    if not host:
        return None
    host = host.lower()
    if host.endswith(local_domain):
        sub = host.removesuffix(f".{local_domain}")
        if sub and sub != local_domain:
            return sub.split(".")[0]
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

        # Decode JWT if provided
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            try:
                claims = decode_token(token, tenant)
                request.state.claims = claims
            except Exception as exc:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": f"invalid token: {exc}"},
                )

        # Enforce tenant match ONLY if token has a non-empty 'tid'
        if tenant and request.state.claims:
            tid = str(request.state.claims.get("tid", "") or "").strip().lower()
            if tid and tid != tenant.lower():
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "token tenant mismatch"},
                )

        # Admin paths require owner role
        if request.url.path.startswith("/admin"):
            if not request.state.claims:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "missing token"},
                )
            try:
                ensure_role(request.state.claims, "owner")
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        # Always return downstream response
        return await call_next(request)


