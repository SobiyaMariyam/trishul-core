# app/api/rudra.py
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import List, Optional
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

from app.services.rudra_forecast import train_and_predict, utcnow

router = APIRouter(prefix="/rudra", tags=["rudra"])

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("CORE_DB")]

class UsageIn(BaseModel):
    usage: List[float] = Field(..., min_items=2)

class ForecastOut(BaseModel):
    amount_pred: float
    slope: float
    created_at: str

class ConfigIn(BaseModel):
    enforce_mfa: bool = True
    public_s3: bool = False

@router.post("/cloud/mock-usage")
async def mock_usage(payload: UsageIn, request: Request):
    tenant = request.state.tenant
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    db[f"{tenant}_costs"].insert_one({
        "kind": "mock_usage",
        "values": payload.usage,
        "created_at": utcnow(),
    })
    return {"ok": True, "count": len(payload.usage)}

@router.get("/cloud/forecast", response_model=ForecastOut)
async def forecast(request: Request):
    tenant = request.state.tenant
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    # latest mock usage
    rec = db[f"{tenant}_costs"].find_one({"kind":"mock_usage"}, sort=[("created_at", DESCENDING)])
    if not rec or not rec.get("values"):
        raise HTTPException(status_code=404, detail="no usage data")
    pred, slope = train_and_predict(rec["values"])
    out = {
        "amount_pred": round(pred, 2),
        "slope": round(slope, 4),
        "created_at": utcnow(),
    }
    db[f"{tenant}_costs"].insert_one({
        "kind": "forecast",
        **out
    })
    return {**out, "created_at": out["created_at"].isoformat()}

@router.post("/cloud/configcheck")
async def config_check(cfg: ConfigIn, request: Request):
    tenant = request.state.tenant
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    issues = []
    if not cfg.enforce_mfa:
        issues.append("MFA not enforced")
    if cfg.public_s3:
        issues.append("S3 buckets public")
    db[f"{tenant}_audit_logs"].insert_one({
        "event":"configcheck",
        "issues": issues,
        "created_at": utcnow(),
    })
    return {"status": "issues" if issues else "ok", "issues": issues}
