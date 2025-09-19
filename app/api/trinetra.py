from bson.json_util import dumps
from starlette.responses import Response
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Request, Depends
from typing import Dict, Any
from app.deps import get_qc_repo, get_db

router = APIRouter()

def _tenant_from(request: Request) -> str:
    host = request.headers.get("Host", "default")
    return host.split(".")[0] if host else "default"

@router.post("/trinetra/qc/upload")
async def qc_upload(
    request: Request,
    file: UploadFile = File(...),
    repo = Depends(get_qc_repo),  # repo handles in-memory vs mongo
):
    tenant = _tenant_from(request)
    content = await file.read()
    doc: Dict[str, Any] = {
        "tenant": tenant,
        "filename": file.filename,
        "size": len(content),
        "mime": file.content_type,
        "qc": {"ok": True, "reason": "dummy-pass"},
        "ts": datetime.utcnow().isoformat() + "Z",
    }
    repo.store(tenant, doc)
    return {"stored": True}

@router.get("/trinetra/qc/results")
async def qc_results(
    request: Request,
    repo = Depends(get_qc_repo),
):
    tenant = _tenant_from(request)
    # IMPORTANT: return a raw list as the tests expect
    return Response(dumps(list(repo.list(tenant))), media_type="application/json")

from fastapi import Body
from bson.json_util import dumps
from starlette.responses import Response
from fastapi import Depends, Request
from app.deps import get_db

@router.post("/trinetra/qc/seed")
async def trinetra_qc_seed(request: Request, db=Depends(get_db), items: list[dict]=Body(...)):
    tenant = (getattr(getattr(request,"state",None),"tenant",None) or request.headers.get("Host","default")).split(".")[0]
    col = db[f"{tenant}_qc"]
    if isinstance(items, dict):
        items = [items]
    res = col.insert_many(items)
    return Response(dumps({"inserted": len(res.inserted_ids)}), media_type="application/json")

# --- pagination for QC results ---
from app.common.params import LimitParam, SkipParam, clamp_limit_skip

def _qc_set_paging_headers(response, limit, skip):
    try:
        L,S = clamp_limit_skip(limit, skip)
        response.headers["X-Limit"] = str(L)
        response.headers["X-Skip"]  = str(S)
    except Exception:
        pass


