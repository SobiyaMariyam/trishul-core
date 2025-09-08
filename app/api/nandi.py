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
from datetime import datetime

@router.post("/nandi/email/send")
async def nandi_email_send(request: Request, db=Depends(get_db), msg: dict = Body(...)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
    col = db[f"{tenant}_nandi_emails"]
    doc = {
        "to": msg.get("to"),
        "subject": msg.get("subject"),
        "body": msg.get("body", ""),
        "ts": datetime.utcnow().isoformat()+"Z"
    }
    col.insert_one(doc)
    return {"ok": True, "queued": True, "to": doc["to"]}

@router.get("/nandi/email/outbox")
async def nandi_email_outbox(request: Request, db=Depends(get_db)):
    tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
    col = db[f"{tenant}_nandi_emails"]
    docs = list(col.find().sort("ts",-1).limit(10))
    return {"outbox": docs}
from fastapi import Body

@router.post("/nandi/notify")
async def nandi_notify(payload: dict = Body(...)):
    """
    Send an email via SendGrid.
    Body JSON:
      { "to": "<recipient@email>", "subject": "...", "body": "..." }
    Uses SENDGRID_API_KEY from environment.
    """
    import os
    try:
        to = payload.get("to")
        subject = payload.get("subject", "Trishul Notification")
        body = payload.get("body", "Hello from Nandi.")

        if not to:
            return {"sent": False, "error": "missing 'to' address"}

        api_key = os.environ.get("SENDGRID_API_KEY")
        if not api_key:
            return {"sent": False, "error": "SENDGRID_API_KEY not set"}

        # Lazy import to avoid global dependency if unused
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        # IMPORTANT: From must be your verified sender
        message = Mail(
            from_email="trishul.ai825@gmail.com",
            to_emails=to,
            subject=subject,
            html_content=f"<p>{body}</p>"
        )

        sg = SendGridAPIClient(api_key)
        resp = sg.send(message)
        ok = 200 <= resp.status_code < 300
        return {"sent": ok, "status": resp.status_code}
    except Exception as e:
        return {"sent": False, "error": str(e)}
