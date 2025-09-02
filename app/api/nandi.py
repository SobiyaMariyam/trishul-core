from fastapi import APIRouter, Depends, Request
from app.deps import get_db

router = APIRouter()

# Test-safe: no MongoClient at import time. Uses get_db(), which the tests
# override with an in-memory dummy database.

@router.get("/nandi/health")
async def nandi_health():
    return {"ok": True}

@router.get("/nandi/events")
async def nandi_events(request: Request, db = Depends(get_db)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host", "default")).split(".")[0]
    # Return whatever is in the dummy DB; tests can assert shape without hitting real Mongo.
    items = list(db[f"{tenant}_events"].find({}))
    return {"results": items}
