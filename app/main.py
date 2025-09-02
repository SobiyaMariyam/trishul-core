from fastapi import FastAPI, Request
from app.middleware.tenancy_middleware import TenancyMiddleware
from app.middleware.ratelimit import init_rate_limit, limiter
from app.api import auth_routes, protected_routes, admin, kavach, rudra, trinetra, nandi

app = FastAPI(title="Trishul Core")

# middleware
app.add_middleware(TenancyMiddleware)
init_rate_limit(app)

# Public
@app.get("/health")
async def health():
    return {"ok": True}

# Dummy endpoint with 5/min limit
@app.get("/dummy")
@limiter.limit("5/minute")
async def dummy(request: Request):
    return {"ok": True, "msg": "dummy endpoint success"}

# Routers
app.include_router(auth_routes.router)       # /auth/*
app.include_router(protected_routes.router)  # /admin/health etc.
app.include_router(admin.router)             # /admin/stats
app.include_router(kavach.router)            # /kavach/*
app.include_router(rudra.router)             # /rudra/*
app.include_router(trinetra.router)          # /trinetra/*
app.include_router(nandi.router)             # /nandi/*
