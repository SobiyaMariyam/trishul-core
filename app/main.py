from fastapi import FastAPI, Request
from app.middleware.tenancy_middleware import TenancyMiddleware
from app.middleware.ratelimit import init_rate_limit, limiter
from app.api import auth_routes, protected_routes

app = FastAPI(title="Trishul Core")

# middleware
app.add_middleware(TenancyMiddleware)
init_rate_limit(app)

# Public
@app.get("/health")
async def health():
    return {"ok": True}

# Dummy endpoint with 5/min limit (must accept request for SlowAPI)
@app.get("/dummy")
@limiter.limit("5/minute")
async def dummy(request: Request):
    return {"ok": True, "msg": "dummy endpoint success"}

# Routers
app.include_router(auth_routes.router)
app.include_router(protected_routes.router)
app.include_router(protected_routes.admin_router)
