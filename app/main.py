# app/main.py
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from bson import json_util
from prometheus_fastapi_instrumentator import Instrumentator

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from app.middleware.jwt_guard import JWTGuardMiddleware
from app.middleware.tenancy_middleware import TenancyMiddleware
from app.middleware.ratelimit import limiter, init_rate_limit

from app.common.observability import setup_logging, ObservabilityMiddleware

from app.api import (
    auth_routes,
    protected_routes,
    admin,
    kavach,
    rudra,
    trinetra,
    nandi,
    auth_refresh,
    _refresh_diag,
    jobs,
)

# ---- Rate-limit handler fallback ---------------------------------------------
try:
    from slowapi.errors import rate_limit_exceeded_handler as rate_limit_handler
except Exception:
    try:
        from slowapi.errors import _rate_limit_exceeded_handler as rate_limit_handler  # type: ignore
    except Exception:  # last-resort tiny handler
        async def rate_limit_handler(request, exc):
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

# ---- Mongo-safe JSON renderer ------------------------------------------------
class MongoJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json_util.dumps(content).encode("utf-8")

# ---- App bootstrap -----------------------------------------------------------
load_dotenv()
setup_logging()

app = FastAPI(
    default_response_class=MongoJSONResponse,
    title="Trishul Core",
)

# ---- JWT guard ---------------------------------------------------------------
app.add_middleware(JWTGuardMiddleware)

# ---- CORS -------------------------------------------------------------------
env_allowed = os.getenv("ALLOWED_ORIGINS")
allowed_from_env = [o.strip() for o in env_allowed.split(",")] if env_allowed else []

DEFAULT_ALLOWED = [
    "https://app.trishul.cloud",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

_ALLOWED_ORIGINS = list({*DEFAULT_ALLOWED, *allowed_from_env})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Request-ID"],
    max_age=600,
)

# ---- Rate limiting + tenancy -------------------------------------------------
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(TenancyMiddleware)
init_rate_limit(app)

# ---- Health ------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"ok": True}

# ---- Routers ----------------------------------------------------------------
app.include_router(auth_routes.router)
app.include_router(protected_routes.router)
app.include_router(admin.router)
app.include_router(kavach.router)
app.include_router(rudra.router)
app.include_router(trinetra.router)
app.include_router(nandi.router)
app.include_router(jobs.router)              # background jobs
app.include_router(auth_refresh.router)      # /auth/refresh
app.include_router(_refresh_diag.router)     # diagnostics

# ---- Observability (request IDs + audit log) --------------------------------
app.add_middleware(ObservabilityMiddleware)

# ---- Metrics ----------------------------------------------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)