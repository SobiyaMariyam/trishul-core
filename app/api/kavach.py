# app/api/kavach.py
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
import os

from app.middleware.ratelimit import limiter
from app.services.kavach_runner import run_nmap_or_mock

router = APIRouter(prefix="/kavach", tags=["kavach"])

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
CORE_DB = os.getenv("CORE_DB")

client = MongoClient(MONGO_URI)
db = client[CORE_DB]

class StartScanIn(BaseModel):
    target: str = Field(..., min_length=3)

class ScanOut(BaseModel):
    id: str
    target: str
    status: str
    created_at: str
    bytes_xml: int

@router.post("/scan/start")
@limiter.limit("5/minute")
async def start_scan(payload: StartScanIn, request: Request):
    tenant = request.state.tenant
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    target = payload.target.strip()

    status_str, raw_xml, pdf_b64 = run_nmap_or_mock(target)
    doc = {
        "tenant": tenant,
        "target": target,
        "status": status_str,
        "created_at": datetime.now(timezone.utc),
        "raw_xml": raw_xml,
        "report_pdf_b64": pdf_b64,  # prototype stores inline for simplicity
    }
    res = db[f"{tenant}_scans"].insert_one(doc)
    return {"scan_id": str(res.inserted_id), "status": status_str}

@router.get("/scan/history", response_model=List[ScanOut])
async def scan_history(request: Request, limit: int = 10):
    tenant = request.state.tenant
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    cur = db[f"{tenant}_scans"].find({}, sort=[("created_at", DESCENDING)], limit=limit)
    out = []
    for d in cur:
        out.append({
            "id": str(d.get("_id")),
            "target": d.get("target"),
            "status": d.get("status"),
            "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
            "bytes_xml": len((d.get("raw_xml") or "")),
        })
    return out
