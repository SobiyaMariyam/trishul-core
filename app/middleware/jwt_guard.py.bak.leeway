from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import jwt
import re
import os

# SECRET from settings or env (fallback for dev)
try:
    from app.core.config import settings  # type: ignore
    SECRET = getattr(settings, "SECRET_KEY", None)
except Exception:
    SECRET = None
if not SECRET:
    SECRET = os.getenv("SECRET_KEY", "changeme")

def _tenant_from_host(host: str) -> str | None:
    # expect "<tenant>.lvh.me" or "<tenant>.<domain>"
    if not host:
        return None
    # strip port
    host = host.split(":", 1)[0].strip().lower()
    parts = host.split(".")
    if len(parts) < 2:
        return None
    return parts[0] or None

class JWTGuardMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive=receive)
        host = request.headers.get("host", "")
        tenant = _tenant_from_host(host)

        # only guard tenant subdomains; skip if we can't parse a tenant
        if tenant:
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1].strip()
                try:
                    # require exp & aud; HS256 by default
                    jwt.decode(
                        token,
                        SECRET,
                        algorithms=["HS256"],
                        audience=tenant,
                        options={"require": ["exp", "aud"]},
                    )
                except Exception:
                    res = JSONResponse(
                        status_code=401,
                        content={"detail": "invalid token: audience/expiry check failed"},
                    )
                    return await res(scope, receive, send)

        return await self.app(scope, receive, send)
