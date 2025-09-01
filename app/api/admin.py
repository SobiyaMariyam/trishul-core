from fastapi import APIRouter, Request
from pymongo import MongoClient
import os
from dotenv import load_dotenv

router = APIRouter(prefix="/admin", tags=["admin"])

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
CORE_DB = os.getenv("CORE_DB")

client = MongoClient(MONGO_URI)
db = client[CORE_DB]

@router.get("/stats")
async def get_stats(request: Request):
    tenant = request.state.tenant
    if not tenant:
        return {"error": "tenant missing"}

    scan_count = db[f"{tenant}_scans"].count_documents({})
    qc_count   = db[f"{tenant}_qc_results"].count_documents({})
    last_forecast = db[f"{tenant}_costs"].find_one(sort=[("created_at", -1)])

    return {
        "tenant": tenant,
        "scan_count": scan_count,
        "qc_results": qc_count,
        "last_forecast": last_forecast["amount_pred"] if last_forecast else None,
    }
