from fastapi import FastAPI, Request
from app.middleware.tenancy import tenancy_middleware
from app.api.auth_routes import router as auth_router
from app.api.protected_routes import router as protected_router

app = FastAPI(title="Trishul Core API")

@app.middleware("http")
async def tenancy(request: Request, call_next):
    return await tenancy_middleware(request, call_next)

# Public-ish (still tenant-scoped via Host): auth
app.include_router(auth_router)

# Protected endpoints
app.include_router(protected_router)

@app.get("/health")
def health():
    return {"ok": True}
