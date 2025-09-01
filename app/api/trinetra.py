from fastapi import APIRouter, File, UploadFile, Request, HTTPException, status
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
from datetime import datetime, timezone
import base64, os

router = APIRouter(prefix="/trinetra", tags=["trinetra"])

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("CORE_DB")]

def _utcnow():
    return datetime.now(timezone.utc)

@router.post("/qc/upload")
async def qc_upload(request: Request, image: UploadFile = File(...)):
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    content = await image.read()
    # mock inference result (delegate later)
    result = {"ok": True, "defect": False, "confidence": 0.97, "filename": image.filename}
    db[f"{tenant}_qc_results"].insert_one({
        "created_at": _utcnow(),
        "result": result,
        # store only a prefix to keep the doc small in prototype
        "image_b64": base64.b64encode(content).decode("ascii")[:1024]
    })
    return result

@router.get("/qc/results")
async def qc_results(request: Request, limit: int = 5):
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant missing")
    cur = db[f"{tenant}_qc_results"].find({}, sort=[("created_at", DESCENDING)], limit=limit)
    out = []
    for d in cur:
        out.append({
            "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
            "result": d.get("result"),
        })
    return out

# Keep echo for quick manual tests
@router.post("/qc/echo")
async def echo_upload(request: Request, image: UploadFile = File(...)):
    content = await image.read()
    tenant = getattr(request.state, "tenant", None)
    return {"filename": image.filename, "size": len(content), "tenant": tenant}
