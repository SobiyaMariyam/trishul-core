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
    try:
        logger.info("Application starting up...")
        yield
    except Exception as e:
        logger.error(f"Application error during lifespan: {e}")
        raise
    finally:
        logger.info("Application shutting down...")

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
try:
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
except Exception as e:
    logger.error(f"Error loading routers: {e}")
    # Continue without problematic routers for now

# ---- Observability (request IDs + audit log) --------------------------------
app.add_middleware(ObservabilityMiddleware)

# ---- Metrics ----------------------------------------------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

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
    logger.info("Cleaning up resources...")
    # Close database connections, file handles, etc.
    try:
        if client is not None:
            client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Register cleanup function
atexit.register(cleanup)

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)