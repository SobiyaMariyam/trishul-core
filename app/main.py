# app/main.py - CLEAN VERSION FOR GITHUB ACTIONS
import os
from dotenv import load_dotenv
load_dotenv()

CI_MODE = os.getenv("USE_INMEMORY_DB") == "1"
GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true"

if CI_MODE:
    print("[CI-DEBUG] Starting Trishul in CI mode", flush=True)
    if GITHUB_ACTIONS:
        print("[CI-DEBUG] GitHub Actions detected", flush=True)
        
        # Write process ID for GitHub Actions monitoring
        import threading
        import time
        
        def write_process_id():
            """Write process ID for GitHub Actions to monitor"""
            while True:
                try:
                    with open("api_process_id.txt", "w") as f:
                        f.write(str(os.getpid()))
                    time.sleep(5)
                except:
                    pass
        
        pid_thread = threading.Thread(target=write_process_id, daemon=True)
        pid_thread.start()

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
