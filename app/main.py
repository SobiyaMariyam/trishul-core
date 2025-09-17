from prometheus_fastapi_instrumentator import Instrumentator
from bson import json_util
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from app.middleware.tenancy_middleware import TenancyMiddleware
from app.middleware.ratelimit import limiter, init_rate_limit
from app.api import auth_routes, protected_routes, admin, kavach, rudra, trinetra, nandi

# Try known handler names; fall back to a tiny custom one
try:
    from slowapi.errors import rate_limit_exceeded_handler as rate_limit_handler
except Exception:
    try:
        from slowapi.errors import _rate_limit_exceeded_handler as rate_limit_handler
    except Exception:
        async def rate_limit_handler(request, exc):
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

class MongoJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json_util.dumps(content).encode("utf-8")

load_dotenv()
app = FastAPI(default_response_class=MongoJSONResponse, title="Trishul Core")
# --- CORS (strict) ---
_allowed = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed if o.strip()],
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","Origin","Accept"],
)
# --- end CORS ---

# Rate limit + tenancy middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(TenancyMiddleware)
init_rate_limit(app)

@app.get("/health")
async def health():
    return {"ok": True}

# Routers
app.include_router(auth_routes.router)
app.include_router(protected_routes.router)
app.include_router(admin.router)
app.include_router(kavach.router)
app.include_router(rudra.router)
app.include_router(trinetra.router)
app.include_router(nandi.router)

# --- Observability (request IDs + audit log) ---
from app.common.observability import setup_logging, ObservabilityMiddleware
app.add_middleware(ObservabilityMiddleware)



