from fastapi import APIRouter, Depends, Request
from app.deps import get_db

router = APIRouter()

# Minimal, test-safe endpoints. No MongoClient at import time.

@router.get("/kavach/health")
async def kavach_health():
    return {"ok": True}

@router.get("/kavach/profile")
async def kavach_profile(request: Request, db = Depends(get_db)):
    # Example read that works with the in-memory dummy DB during tests.
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host", "default")).split(".")[0]
    doc = (db[f"{tenant}_users"].find_one({"role": "owner"}) or {"tenant": tenant, "role": "owner"})
    return doc
