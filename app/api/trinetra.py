from datetime import datetime, timezone
from typing import Dict, Any, List

from bson.json_util import dumps
from starlette.responses import Response
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Request,
    Depends,
    HTTPException,
    Body,
)

from app.deps import get_qc_repo, get_db
from app.common.params import LimitParam, SkipParam, clamp_limit_skip

router = APIRouter()

# --- helpers --------------------------------------------------------------
def _tenant_from(request: Request) -> str:
    host = request.headers.get("Host", "default")
    return host.split(".")[0] if host else "default"

def _qc_set_paging_headers(response: Response, limit: int, skip: int):
    """Attach pagination headers to response (best effort)."""
    try:
        L, S = clamp_limit_skip(limit, skip)
        response.headers["X-Limit"] = str(L)
        response.headers["X-Skip"] = str(S)
    except Exception:
        pass

# --- endpoints ------------------------------------------------------------
@router.post("/trinetra/qc/upload")
async def qc_upload(
    request: Request,
    file: UploadFile = File(...),
    repo=Depends(get_qc_repo),
):
    """
    Upload a QC file. Metadata is stored in repo (in-memory or Mongo).
    """
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
    repo=Depends(get_qc_repo),
):
    """
    Return stored QC results for tenant.
    """
    tenant = _tenant_from(request)
    return Response(
        dumps(list(repo.list(tenant))),
        media_type="application/json",
    )

@router.post("/trinetra/qc/seed")
async def trinetra_qc_seed(
    request: Request,
    db=Depends(get_db),
    items: List[dict] = Body(...),
):
    """
    Seed QC items directly into Mongo for a tenant.
    Includes validation & cleaning.
    """
    tenant = (
        getattr(getattr(request, "state", None), "tenant", None)
        or request.headers.get("Host", "default")
    ).split(".")[0]

    col = db[f"{tenant}_qc"]

    if isinstance(items, dict):
        items = [items]

    # --- begin hardening: validate seed items ---
    if not isinstance(items, list) or len(items) == 0:
        raise HTTPException(status_code=400, detail="items must be a non-empty list")

    cleaned = []
    for it in items:
        if not isinstance(it, dict):
            continue
        fname = it.get("filename") or it.get("name")
        status = (it.get("status") or "ok").lower()
        if fname and status in {"ok", "fail", "warn"}:
            doc = {
                "tenant": tenant,
                "filename": fname,
                "mime": it.get("mime") or "application/octet-stream",
                "size": int(it.get("size") or 0),
                "qc": {
                    "ok": status == "ok",
                    "reason": it.get("reason") or "dummy-pass",
                },
                "ts": datetime.utcnow().replace(tzinfo=timezone.utc),
            }
            cleaned.append(doc)

    if not cleaned:
        raise HTTPException(status_code=400, detail="no valid items to insert")
    # --- end hardening ---

    res = col.insert_many(cleaned)
    return Response(
        dumps({"inserted": len(res.inserted_ids)}),
        media_type="application/json",
    )