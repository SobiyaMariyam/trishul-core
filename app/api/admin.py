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
    last_forecast = safe_get_forecast()

    return {
        "tenant": tenant,
        "scan_count": scan_count,
        "qc_results": qc_results,
        "last_forecast": last_forecast,
    }

@router.get("/admin/health")
async def health_check():
    return {"status": "ok"}
