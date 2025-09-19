import httpx
import os
import json
from bson import json_util
from fastapi import APIRouter, Depends, Request, Body
from bson.json_util import dumps
from starlette.responses import Response
from app.deps import get_db
from datetime import datetime

router = APIRouter()

@router.get("/nandi/events")
async def nandi_events(request: Request, db=Depends(get_db)):
    tenant = (getattr(getattr(request,"state",None),"tenant",None) or request.headers.get("Host","default")).split(".")[0]
    col = db[f"{tenant}_nandi"]
    docs = list(col.find().sort("timestamp", -1))
    return Response(dumps({"results": docs}), media_type="application/json")

@router.post("/nandi/events/seed")
async def nandi_events_seed(request: Request, db=Depends(get_db), events: list[dict]=Body(...)):
    tenant = (getattr(getattr(request,"state",None),"tenant",None) or request.headers.get("Host","default")).split(".")[0]
    col = db[f"{tenant}_nandi"]
    if isinstance(events, dict):
        events = [events]
    for e in events:
        e.setdefault("timestamp", datetime.utcnow().isoformat()+"Z")
    res = col.insert_many(events)
    return Response(dumps({"inserted": len(res.inserted_ids)}), media_type="application/json")
from fastapi import Body
from fastapi.responses import JSONResponse
from datetime import datetime

@router.post("/nandi/email/send")
async def nandi_email_send(request: Request, db=Depends(get_db), msg: dict = Body(...)):
    from datetime import datetime
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]

    # Persist to DB (same collection you've been using)
    col = db[f"{tenant}_nandi_emails"]
    doc = {
        "to": msg.get("to"),
        "subject": msg.get("subject"),
        "body": msg.get("body", ""),
        "ts": datetime.utcnow().isoformat() + "Z"
    }
    try:
        col.insert_one(doc)
    except Exception:
        pass  # don't fail send if db insert has issues

    # Try SendGrid if key is present
    sg_key  = os.getenv("SENDGRID_API_KEY")
    sg_from = (msg.get("from") or os.getenv("SENDGRID_FROM"))  # must be your verified sender
    sent = False
    if sg_key and sg_from and doc.get("to") and doc.get("subject") is not None:
        try:
            payload = {
                "personalizations": [ { "to": [ { "email": doc["to"] } ] } ],
                "from": { "email": sg_from },
                "subject": doc["subject"],
                "content": [ { "type": "text/plain", "value": doc["body"] } ]
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={ "Authorization": f"Bearer {sg_key}", "Content-Type": "application/json" },
                    json=payload
                )
            sent = resp.status_code in (200, 202)
        except Exception:
            sent = False

    return {"ok": True, "queued": True, "sent": sent, "to": doc.get("to")}
@router.get("/nandi/email/outbox")
async def nandi_email_outbox(request: Request, db=Depends(get_db)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
    try:
        coll = db[f"{tenant}_nandi_emails"]
        outbox = list(coll.find({}))
    except Exception:
        outbox = []
    payload = {"results": outbox}
    return JSONResponse(content=json.loads(json_util.dumps(payload)))

