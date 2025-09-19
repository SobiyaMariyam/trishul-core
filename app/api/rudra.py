from fastapi import APIRouter, Request, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.deps import get_db

router = APIRouter()

def _tenant_from(request: Request) -> str:
    return (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]

@router.post("/rudra/cloud/mock-usage")
async def mock_usage(request: Request, payload: Optional[dict] = None, db = Depends(get_db)):
    tenant = _tenant_from(request)
    payload = payload or {}
    usage = payload.get("usage") or [
        {"service":"ec2","hours":120,"rate":0.12},
        {"service":"s3","gb":500,"rate":0.023},
    ]
    try:
        coll = db["rudra_usage"]
        coll.insert_one({
            "tenant": tenant,
            "usage": usage,
            "ts": datetime.utcnow().isoformat()+"Z",
        })
    except Exception:
        # non-fatal for demo / in-memory case
        pass
    return {"usage": usage}

@router.get("/rudra/cloud/forecast")
async def forecast(request: Request, db = Depends(get_db)):
    tenant = _tenant_from(request)
    usage: List[Dict[str, Any]] = []
    try:
        # pick latest usage for this tenant if available
        cur = db["rudra_usage"].find({"tenant": tenant}).sort([("_id", -1)]).limit(1)
        docs = list(cur)
        if docs:
            usage = docs[0].get("usage", [])
    except Exception:
        pass

    if not usage:
        usage = [
            {"service":"ec2","hours":120,"rate":0.12},
            {"service":"s3","gb":500,"rate":0.023},
        ]

    forecast_vals: List[float] = []
    for item in usage:
        if "hours" in item:
            cost = float(item.get("hours", 0)) * float(item.get("rate", 0))
        elif "gb" in item:
            cost = float(item.get("gb", 0)) * float(item.get("rate", 0))
        else:
            cost = 0.0
        forecast_vals.append(max(0.0, cost))

    if not forecast_vals:
        forecast_vals = [0.0]

    total = float(sum(forecast_vals))
    return {"forecast": forecast_vals, "total": total}

@router.post("/rudra/cloud/forecast/save")
async def cloud_forecast_save(request: Request, payload: Optional[dict] = None, db = Depends(get_db)):
    tenant = _tenant_from(request)
    payload = payload or {}

    # use provided series or recompute from latest usage
    series = payload.get("series")
    if series is None:
        # recompute via forecast logic (DRY-ish)
        usage: List[Dict[str, Any]] = []
        try:
            cur = db["rudra_usage"].find({"tenant": tenant}).sort([("_id", -1)]).limit(1)
            docs = list(cur)
            if docs:
                usage = docs[0].get("usage", [])
        except Exception:
            pass

        if not usage:
            usage = [
                {"service":"ec2","hours":120,"rate":0.12},
                {"service":"s3","gb":500,"rate":0.023},
            ]

        series = []
        for item in usage:
            if "hours" in item:
                cost = float(item.get("hours", 0)) * float(item.get("rate", 0))
            elif "gb" in item:
                cost = float(item.get("gb", 0)) * float(item.get("rate", 0))
            else:
                cost = 0.0
            series.append(max(0.0, cost))

        if not series:
            series = [0.0]

    avg = (sum(series) / len(series)) if series else 0.0

    try:
        db["rudra_forecasts"].insert_one({
            "tenant": tenant,
            "value": float(avg),
            "series": [float(x) for x in series],
            "ts": datetime.utcnow().isoformat()+"Z",
        })
    except Exception:
        pass

    return {"ok": True, "avg": float(avg)}
