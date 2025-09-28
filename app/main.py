# app/main.py
import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Immediate CI logging
if os.getenv("USE_INMEMORY_DB") == "1":
    print("[CI-DEBUG] Starting Trishul in CI mode", flush=True)
    print(f"[CI-DEBUG] Python: {sys.executable}", flush=True)
    print(f"[CI-DEBUG] Working dir: {os.getcwd()}", flush=True)

# Core FastAPI imports with error handling
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] FastAPI imports successful", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] FastAPI import failed: {e}", flush=True)
    raise

# BSON and JSON imports
try:
    from bson import json_util
    import json
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] JSON imports successful", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] JSON import failed: {e}", flush=True)
    raise

# Prometheus (optional in CI)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Prometheus import successful", flush=True)
except Exception as e:
    if os.getenv("USE_INMEMORY_DB") == "1":
        print(f"[CI-DEBUG] Prometheus import failed (expected in CI): {e}", flush=True)
    Instrumentator = None

# Rate limiting imports (optional in CI)
try:
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.errors import RateLimitExceeded
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] SlowAPI imports successful", flush=True)
except Exception as e:
    if os.getenv("USE_INMEMORY_DB") == "1":
        print(f"[CI-DEBUG] SlowAPI import failed (expected in CI): {e}", flush=True)
    SlowAPIMiddleware = None
    RateLimitExceeded = Exception

# Middleware imports
try:
    from app.middleware.jwt_guard import JWTGuardMiddleware
    from app.middleware.tenancy_middleware import TenancyMiddleware
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Middleware imports successful", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] Middleware import failed: {e}", flush=True)
    raise

# Rate limiting components (optional)
try:
    from app.middleware.ratelimit import limiter, init_rate_limit
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Rate limit imports successful", flush=True)
except Exception as e:
    if os.getenv("USE_INMEMORY_DB") == "1":
        print(f"[CI-DEBUG] Rate limit import failed (expected in CI): {e}", flush=True)
    limiter = None
    init_rate_limit = lambda app: None

# Observability imports
try:
    from app.common.observability import setup_logging, ObservabilityMiddleware
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Observability imports successful", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] Observability import failed: {e}", flush=True)
    # Create fallback functions
    def setup_logging(): pass
    class ObservabilityMiddleware: pass

# Router imports with error handling
try:
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
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] All router imports successful", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] Router import failed: {e}", flush=True)
    raise

import logging
import sys
from contextlib import asynccontextmanager
from pymongo import MongoClient
import atexit
import signal

# Add comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('api.log')
    ]
)

logger = logging.getLogger(__name__)

# Custom JSON Response for MongoDB BSON objects
class MongoJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json_util.dumps(content).encode("utf-8")

# Rate limit handler
async def rate_limit_handler(request: Request, exc):
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail if hasattr(exc, 'detail') else 'Rate limit exceeded'}"}
    )
    if hasattr(exc, 'retry_after'):
        response.headers["Retry-After"] = str(exc.retry_after) if exc.retry_after else "1"
    return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    startup_success = False
    persistence_task = None
    try:
        if os.getenv("USE_INMEMORY_DB") == "1":
            print("[CI-DEBUG] Application lifespan starting...", flush=True)
        logger.info("Application starting up...")
        
        # Add any startup tasks here with individual error handling
        try:
            # Validate essential components are working
            if os.getenv("USE_INMEMORY_DB") == "1":
                print("[CI-DEBUG] Validating core components...", flush=True)
            logger.info("Validating core components...")
            
            # In CI environment, create a persistence task to keep process alive
            if os.getenv("USE_INMEMORY_DB") == "1":
                import asyncio
                async def maintain_process():
                    """Keep the process alive in CI environments by maintaining async tasks"""
                    try:
                        counter = 0
                        while True:
                            await asyncio.sleep(10)  # Check every 10 seconds
                            counter += 1
                            if counter % 6 == 0:  # Log every minute
                                print(f"[CI-DEBUG] Process persistence check #{counter//6}", flush=True)
                    except asyncio.CancelledError:
                        print("[CI-DEBUG] Process persistence task cancelled", flush=True)
                        raise
                    except Exception as e:
                        print(f"[CI-DEBUG] Process persistence error: {e}", flush=True)
                        
                persistence_task = asyncio.create_task(maintain_process())
                print("[CI-DEBUG] Process persistence task started", flush=True)
                
            startup_success = True
        except Exception as startup_error:
            logger.error(f"Startup validation failed: {startup_error}")
            # Don't raise - let the app start anyway
            
        logger.info("Application startup complete")
        if os.getenv("USE_INMEMORY_DB") == "1":
            print("[CI-DEBUG] Application startup complete, yielding control...", flush=True)
        
        yield
        
    except Exception as lifespan_error:
        logger.error(f"Application error during lifespan: {lifespan_error}")
        import traceback
        logger.error(f"Lifespan traceback: {traceback.format_exc()}")
        # Don't re-raise in CI environment to prevent early termination
        if os.getenv("USE_INMEMORY_DB") != "1":
            raise
        else:
            logger.warning("Suppressing lifespan error in CI environment")
            if os.getenv("USE_INMEMORY_DB") == "1":
                print(f"[CI-DEBUG] Lifespan error suppressed: {lifespan_error}", flush=True)
            
    finally:
        # Shutdown
        try:
            if os.getenv("USE_INMEMORY_DB") == "1":
                print("[CI-DEBUG] Application shutting down...", flush=True)
            logger.info("Application shutting down...")
            
            # Cancel persistence task if it exists
            if persistence_task and not persistence_task.done():
                persistence_task.cancel()
                try:
                    await persistence_task
                except asyncio.CancelledError:
                    pass
                if os.getenv("USE_INMEMORY_DB") == "1":
                    print("[CI-DEBUG] Process persistence task cancelled", flush=True)
            
            # Add any cleanup tasks here
            logger.info("Application shutdown complete")
            if os.getenv("USE_INMEMORY_DB") == "1":
                print("[CI-DEBUG] Application shutdown complete", flush=True)
        except Exception as shutdown_error:
            logger.error(f"Error during shutdown: {shutdown_error}")
            # Don't let shutdown errors propagate

app = FastAPI(
    default_response_class=MongoJSONResponse,
    title="Trishul Core",
    lifespan=lifespan,
)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# ---- JWT guard ---------------------------------------------------------------
try:
    app.add_middleware(JWTGuardMiddleware)
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] JWT middleware added", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] Failed to add JWT middleware: {e}", flush=True)

# ---- CORS -------------------------------------------------------------------
try:
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
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] CORS middleware added", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] Failed to add CORS middleware: {e}", flush=True)

# ---- Rate limiting + tenancy -------------------------------------------------
# Only enable rate limiting if not in CI/testing environment
if os.getenv("USE_INMEMORY_DB") != "1" and limiter is not None and SlowAPIMiddleware is not None:
    try:
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)
        app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
        init_rate_limit(app)
        logger.info("Rate limiting enabled")
    except Exception as e:
        logger.error(f"Failed to setup rate limiting: {e}")
else:
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Rate limiting disabled for CI/testing environment", flush=True)
    else:
        logger.info("Rate limiting disabled (components not available)")

# Always enable tenancy middleware as it's lightweight
try:
    app.add_middleware(TenancyMiddleware)
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Tenancy middleware added", flush=True)
except Exception as e:
    print(f"[CI-DEBUG] Failed to add tenancy middleware: {e}", flush=True)

# ---- Health ------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"ok": True}

# ---- Routers ----------------------------------------------------------------
# Load routers individually to isolate import errors
if os.getenv("USE_INMEMORY_DB") == "1":
    print("[CI-DEBUG] Starting router loading...", flush=True)

try:
    app.include_router(auth_routes.router)
    logger.info("[OK] Loaded auth_routes router")
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] auth_routes loaded", flush=True)
except Exception as e:
    logger.error(f"[FAIL] Failed to load auth_routes: {e}")
    if os.getenv("USE_INMEMORY_DB") == "1":
        print(f"[CI-DEBUG] auth_routes failed: {e}", flush=True)

try:
    app.include_router(protected_routes.router)
    logger.info("[OK] Loaded protected_routes router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load protected_routes: {e}")

try:
    app.include_router(admin.router)
    logger.info("[OK] Loaded admin router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load admin: {e}")

try:
    app.include_router(kavach.router)
    logger.info("[OK] Loaded kavach router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load kavach: {e}")

try:
    app.include_router(rudra.router)
    logger.info("[OK] Loaded rudra router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load rudra: {e}")

try:
    app.include_router(trinetra.router)
    logger.info("[OK] Loaded trinetra router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load trinetra: {e}")

try:
    app.include_router(nandi.router)
    logger.info("[OK] Loaded nandi router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load nandi: {e}")

try:
    app.include_router(jobs.router)
    logger.info("[OK] Loaded jobs router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load jobs: {e}")

try:
    app.include_router(auth_refresh.router)
    logger.info("[OK] Loaded auth_refresh router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load auth_refresh: {e}")

try:
    app.include_router(_refresh_diag.router)
    logger.info("[OK] Loaded refresh_diag router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load refresh_diag: {e}")

# ---- Observability (request IDs + audit log) --------------------------------
# app.add_middleware(ObservabilityMiddleware)  # Temporarily disabled for debugging

# ---- Metrics ----------------------------------------------------------------
# Only enable metrics collection if not in CI/testing environment
if os.getenv("USE_INMEMORY_DB") != "1":
    try:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
        logger.info("Prometheus metrics enabled")
    except Exception as e:
        logger.warning(f"Failed to enable metrics: {e}")
else:
    logger.info("Prometheus metrics disabled for CI/testing environment")

# ---- MongoDB Connection ------------------------------------------------------
client = None
try:
    if os.getenv("USE_INMEMORY_DB") == "1":
        logger.info("Using in-memory database mode")
        client = None
    else:
        client = MongoClient(
            os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
            serverSelectionTimeoutMS=5000,  # Timeout after 5 seconds
            connectTimeoutMS=10000,
            maxPoolSize=10,
            retryWrites=True
        )
        # Test connection
        client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    # Don't exit, but handle gracefully
    client = None

def cleanup():
    try:
        logger.info("Cleaning up resources...")
        # Close database connections, file handles, etc.
        try:
            if client is not None:
                client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
            
        # Add any other cleanup tasks here with individual error handling
        logger.info("Cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        # Don't let cleanup errors cause the process to fail

# Register cleanup function
# Register cleanup function only if not in CI environment
if os.getenv("USE_INMEMORY_DB") != "1":
    atexit.register(cleanup)
    logger.info("Cleanup handler registered")
else:
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Cleanup handler disabled for CI/testing environment", flush=True)
    else:
        logger.info("Cleanup handler disabled for CI/testing environment")

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    if os.getenv("USE_INMEMORY_DB") == "1":
        print(f"[CI-DEBUG] Signal {signum} received but ignoring in CI mode", flush=True)
        return  # Don't exit in CI mode
    cleanup()
    sys.exit(0)

# Only register signal handlers if not in CI/testing environment
if os.getenv("USE_INMEMORY_DB") != "1":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    logger.info("Signal handlers registered")
else:
    if os.getenv("USE_INMEMORY_DB") == "1":
        print("[CI-DEBUG] Signal handlers disabled for CI/testing environment", flush=True)
    else:
        logger.info("Signal handlers disabled for CI/testing environment")