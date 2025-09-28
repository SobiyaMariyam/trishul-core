# Trishul Core — AI Assistant Instructions

## Project Overview
**Trishul** is a multi-tenant FastAPI security platform with 5 core modules: **Kavach** (security scanning), **Rudra** (cloud forecasting), **Trinetra** (QC/image analysis), **Nandi** (email), and **Admin** (management). It uses MongoDB with database-per-tenant isolation and JWT-based authentication.

## Architecture Patterns

### Multi-Tenancy via Host Headers
- **Tenant Discovery**: Extract tenant from `Host` header (e.g., `tenant1.lvh.me` → `tenant1`)
- **Data Isolation**: MongoDB collections prefixed with tenant (`{tenant}_scans`, `{tenant}_users`)
- **Middleware**: `TenancyMiddleware` handles tenant extraction and JWT validation automatically
- **Testing**: Use `$env:HOST = "tenant1.lvh.me"` and test helper `Invoke-TrishulTest`

### Database Abstraction
- **Production**: Real MongoDB via `app/db/manager.py`
- **Testing/CI**: In-memory collections via `app/deps.py` when `USE_INMEMORY_DB=1`
- **Pattern**: Always use `get_db()` dependency, never direct DB connections

### Authentication & RBAC
- **JWT Structure**: Include `tid` (tenant), `sub` (user), `role` (analyst/owner/admin)
- **Role Hierarchy**: `analyst < owner < admin` (see `app/auth/rbac.py`)
- **Enforcement**: Use `@requires_role("owner")` decorator on protected endpoints

## Development Workflows

### Environment Setup
```bash
# Required environment variables
SECRET_KEY=dev-secret-for-ci
TENANT_DOMAIN=tenant1.lvh.me
USE_INMEMORY_DB=1  # For testing/development
```

### Running Locally
```bash
# Start API server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Run all tests
pytest

# Run specific API tests (PowerShell)
$env:HOST = "tenant1.lvh.me"; .\tests\Kavach.Api.Tests.ps1
```

### Code Quality
```bash
# Format code
black app/ tests/
ruff check --fix app/ tests/

# Type checking
mypy app/
```

## API Module Patterns

### Standard Router Structure
```python
# app/api/{module}.py
from fastapi import APIRouter, Request, Depends
from app.deps import get_db
from app.middleware.ratelimit import limiter

router = APIRouter()

@router.post("/module/action")
@limiter.limit("5/minute")  # Rate limiting on write operations
async def module_action(request: Request, db=Depends(get_db)):
    tenant = _tenant_from_req(request)  # Extract tenant
    # Tenant-scoped database operations
    return {"result": "success"}
```

### Tenant-Scoped Database Operations
```python
def _tenant_from_req(request: Request) -> str:
    """Extract tenant from request state or Host header"""
    return (getattr(getattr(request, "state", None), "tenant", None) 
            or request.headers.get("Host", "default")).split(".")[0]

# Always prefix collections with tenant
collection = db[f"{tenant}_scans"]
```

### Response Patterns
- **Success**: Return dict/list directly (auto-serialized by `MongoJSONResponse`)
- **MongoDB**: Use `bson.json_util.dumps()` for complex BSON objects
- **Files**: Return `FastAPI.Response` with appropriate `media_type`

## Testing Conventions

### PowerShell Test Structure
```powershell
# Use shared helper for consistent API calls
. "tests/_helpers.ps1"
$result = Invoke-TrishulTest -Path '/health' -Method GET
```

### Python Test Patterns
```python
# tests/test_*.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_endpoint_requires_tenant(client):
    # Test with proper Host header
    response = client.get("/api/endpoint", headers={"Host": "tenant1.lvh.me"})
```

## Common Integration Points

### Rate Limiting
- **Scan Operations**: 5/minute limit on `/kavach/scan/start`
- **Implementation**: `slowapi` with Redis backend (production) or memory (testing)
- **Testing**: May be disabled in test environments

### File Uploads
- **Pattern**: `multipart/form-data` with key `image` (Trinetra QC)
- **Storage**: Mock in-memory for testing, real storage in production

### Background Jobs
- **Scheduler**: APScheduler for periodic tasks
- **Pattern**: Jobs registered in `app/jobs.py`, exposed via `/jobs` endpoints

## Key Files Reference
- **Main App**: `app/main.py` - FastAPI setup, middleware chain, router registration
- **Configuration**: `app/core/config.py` - Pydantic settings with env var support
- **Dependencies**: `app/deps.py` - Database abstraction (real vs in-memory)
- **Tenancy**: `app/middleware/tenancy_middleware.py` - Multi-tenant request handling
- **Testing**: `tests/_helpers.ps1` - PowerShell API testing utilities
- **CI Setup**: `scripts/start_api_ci.py` - Automated server startup for CI

## Development Anti-Patterns
❌ **Don't** hardcode tenant names - always extract from request  
❌ **Don't** bypass `get_db()` dependency - breaks testing isolation  
❌ **Don't** forget `Host` header in API calls - breaks tenant routing  
❌ **Don't** use raw MongoDB client - use the abstracted collections  
❌ **Don't** skip rate limiting decorators on write operations