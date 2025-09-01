from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
from datetime import datetime, timezone
import os

router = APIRouter(prefix="/nandi", tags=["nandi"])

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("CORE_DB")]

class SendIn(BaseModel):
    to_email: EmailStr
    subject: str = Field(..., min_length=1)
    body_html: str = Field(..., min_length=1)

def _utcnow():
    return datetime.now(timezone.utc)

@router.post("/send")
async def send(payload: SendIn, request: Request):
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    # mocked provider
    code, provider_msg = 202, "mocked"
    db[f"{tenant}_email_logs"].insert_one({
        "to": payload.to_email,
        "subject": payload.subject,
        "body_preview": payload.body_html[:200],
        "status": code,
        "provider_msg": provider_msg,
        "created_at": _utcnow(),
    })
    return {"status": code, "message": "sent"}

@router.get("/logs")
async def logs(request: Request, limit: int = 5):
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    cur = db[f"{tenant}_email_logs"].find({}, sort=[("created_at", DESCENDING)], limit=limit)
    out = []
    for d in cur:
        out.append({
            "to": d.get("to"),
            "subject": d.get("subject"),
            "status": d.get("status"),
            "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
        })
    return out
