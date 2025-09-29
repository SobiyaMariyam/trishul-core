# app/main.py - CLEAN VERSION FOR GITHUB ACTIONS
import os
from dotenv import load_dotenv
load_dotenv()

CI_MODE = os.getenv("USE_INMEMORY_DB") == "1"
if CI_MODE:
    print("[CI-DEBUG] Starting Trishul in CI mode", flush=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.tenancy_middleware import TenancyMiddleware

app = FastAPI(title="Trishul Multi-Tenant Security Platform", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenancyMiddleware)

from app.api import auth_routes, kavach, rudra, trinetra, nandi, admin, jobs_api
app.include_router(auth_routes.router, prefix="/api", tags=["auth"])
app.include_router(kavach.router, prefix="/api", tags=["kavach"])
app.include_router(rudra.router, prefix="/api", tags=["rudra"])
app.include_router(trinetra.router, prefix="/api", tags=["trinetra"])
app.include_router(nandi.router, prefix="/api", tags=["nandi"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(jobs_api.router, prefix="/api", tags=["jobs"])

@app.get("/health")
async def health_check():
    if CI_MODE:
        print(f"[CI-DEBUG] Health check - PID {os.getpid()}", flush=True)
    return {"status": "healthy", "service": "trishul-api", "version": "2.0.0"}

@app.get("/")
async def root():
    return {"message": "Trishul API", "version": "2.0.0"}

if CI_MODE:
    print("[CI-DEBUG] API initialized", flush=True)
