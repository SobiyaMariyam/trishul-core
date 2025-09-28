# app/main.py
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from bson import json_util
import json
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
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )
    response.headers["Retry-After"] = str(exc.retry_after) if exc.retry_after else "1"
    return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    startup_success = False
    keep_alive_task = None
    try:
        logger.info("Application starting up...")
        
        # Add any startup tasks here with individual error handling
        try:
            # Validate essential components are working
            logger.info("Validating core components...")
            
            # In CI environment, create a keep-alive task to prevent premature exit
            if os.getenv("USE_INMEMORY_DB") == "1":
                import asyncio
                async def keep_alive():
                    """Keep the event loop alive in CI environments"""
                    while True:
                        await asyncio.sleep(30)  # Wake up every 30 seconds
                        logger.debug("Keep-alive heartbeat")
                        
                keep_alive_task = asyncio.create_task(keep_alive())
                logger.info("Keep-alive task started for CI environment")
                
            startup_success = True
        except Exception as startup_error:
            logger.error(f"Startup validation failed: {startup_error}")
            # Don't raise - let the app start anyway
            
        logger.info("Application startup complete")
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
            
    finally:
        # Shutdown
        try:
            logger.info("Application shutting down...")
            
            # Cancel keep-alive task if it exists
            if keep_alive_task and not keep_alive_task.done():
                keep_alive_task.cancel()
                try:
                    await keep_alive_task
                except asyncio.CancelledError:
                    pass
                logger.info("Keep-alive task cancelled")
                
            # Add any cleanup tasks here
            logger.info("Application shutdown complete")
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
# Only enable rate limiting if not in CI/testing environment
if os.getenv("USE_INMEMORY_DB") != "1":
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    init_rate_limit(app)
    logger.info("Rate limiting enabled")
else:
    logger.info("Rate limiting disabled for CI/testing environment")

# Always enable tenancy middleware as it's lightweight
app.add_middleware(TenancyMiddleware)

# ---- Health ------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"ok": True}

# ---- Routers ----------------------------------------------------------------
# Load routers individually to isolate import errors
try:
    app.include_router(auth_routes.router)
    logger.info("[OK] Loaded auth_routes router")
except Exception as e:
    logger.error(f"[FAIL] Failed to load auth_routes: {e}")

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
    logger.info("Cleanup handler disabled for CI/testing environment")

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    cleanup()
    sys.exit(0)

# Only register signal handlers if not in CI/testing environment
if os.getenv("USE_INMEMORY_DB") != "1":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    logger.info("Signal handlers registered")
else:
    logger.info("Signal handlers disabled for CI/testing environment")