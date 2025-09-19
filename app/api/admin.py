from fastapi import APIRouter, Depends, Request
from app.deps import get_db
from app.core.security import require_roles

router = APIRouter()

@router.get("/admin/stats", dependencies=[Depends(require_roles(["owner"]))])
async def get_stats(request: Request, db=Depends(get_db)):
    tenant = request.state.tenant or "public"

    def safe_count(coll):
        try:
            return db[coll].count_documents({})
        except Exception:
            return 0

    def safe_get_forecast():
        try:
            rec = db["forecasts"].find_one({"tenant": tenant}, sort=[("created_at", -1)])
            return float(rec.get("amount_pred", 0.0)) if rec else 0.0
        except Exception:
            cache = getattr(request.app.state, "cache", {})
            return float(cache.get(f"{tenant}:last_forecast", 0.0)) if isinstance(cache, dict) else 0.0

    scan_count = safe_count(f"{tenant}_scans")
    qc_results = safe_count(f"{tenant}_qc_results")
    lastdoc = db[f"{tenant}_rudra_forecasts"].find_one(sort=[("ts", -1)])
    last_forecast = float(lastdoc.get("value", 0.0)) if lastdoc else 0.0

    return {
        "tenant": tenant,
        "scan_count": scan_count,
        "qc_results": qc_results,
        "last_forecast": last_forecast,
    }

@router.get("/admin/health")
async def health_check():
    return {"status": "ok"}
from fastapi import Request, Depends
from datetime import datetime
from app.deps import get_db

@router.post("/admin/seed")
async def admin_seed(request: Request, db=Depends(get_db)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
    scans = db[f"{tenant}_scans"]
    # add 5 dummy scans
    scans.insert_many([{"ts": datetime.utcnow().isoformat()+"Z"} for _ in range(5)])
    # set last_forecast in app cache
    cache = getattr(request.app.state, "cache", None)
    if not isinstance(cache, dict):
        request.app.state.cache = {}
        cache = request.app.state.cache
    cache[f"{tenant}:last_forecast"] = 12.34
    return {"ok": True, "added_scans": 5, "last_forecast": 12.34}
from fastapi import Body
@router.post("/admin/forecast/set")
async def admin_set_forecast(request: Request, value: float = Body(...)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
    cache = getattr(request.app.state, "cache", None)
    if not isinstance(cache, dict):
        request.app.state.cache = {}
        cache = request.app.state.cache
    cache[f"{tenant}:last_forecast"] = float(value)
    return {"ok": True, "last_forecast": float(value)}




from fastapi import Request, Depends
from app.deps import get_db

@router.post("/admin/indexes/create")
async def admin_indexes_create(request: Request, db=Depends(get_db)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
    specs = {
        f"{tenant}_scans": [("ts", 1)],
        f"{tenant}_qc_results": [("ts", 1)],
        f"{tenant}_rudra_forecasts": [("ts", 1)],
        f"{tenant}_nandi": [("timestamp", 1)],
        f"{tenant}_users": [("role", 1)],
    }
    created = {}
    for name, keys in specs.items():
        created[name] = db[name].create_index(keys)
    return {"ok": True, "created": created}

@router.get("/admin/indexes/list")
async def admin_indexes_list(request: Request, db=Depends(get_db)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
    cols = [f"{tenant}_scans", f"{tenant}_qc_results", f"{tenant}_rudra_forecasts", f"{tenant}_nandi", f"{tenant}_users"]
    info = {name: db[name].index_information() for name in cols}
    return {"ok": True, "indexes": info}
from fastapi import Request, HTTPException, status
from app.auth.rbac import ensure_role

# secure override: require bearer + owner role
@router.get("/admin/health")
async def health_check(request: Request):
    claims = getattr(request.state, "claims", None)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")
    ensure_role(claims, "owner")
    return {"status": "ok"}
