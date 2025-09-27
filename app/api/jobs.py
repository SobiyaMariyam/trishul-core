# app/api/jobs.py
from fastapi import APIRouter, HTTPException, Request, status
from typing import Any, Dict
from uuid import uuid4
from app.common.worker import scheduler
from app.jobs import run_kavach_scan, run_trinetra_inference
import time, logging, traceback, asyncio, json

router = APIRouter(prefix="/jobs", tags=["jobs"])

JOBS: Dict[str, Dict[str, Any]] = {}

def _run_and_capture(job_id: str, func, *args, **kwargs):
    rec = JOBS.get(job_id, {"status": "queued"})
    rec["status"] = "running"
    JOBS[job_id] = rec
    try:
        # support both sync and async task functions
        if asyncio.iscoroutinefunction(func):
            result = asyncio.run(func(*args, **kwargs))
        else:
            result = func(*args, **kwargs)
        rec["status"] = "succeeded"
        rec["result"] = result
    except Exception as e:
        logging.error("Job %s failed: %s", job_id, e)
        traceback.print_exc()
        rec["status"] = "failed"
        rec["error"] = str(e)
    finally:
        JOBS[job_id] = rec

def _echo_task(payload: Any):
    time.sleep(2)  # simulate work
    return {"echo": payload, "processed_at": time.time()}

def _require_json(request: Request):
    ctype = request.headers.get("content-type", "")
    if "application/json" not in ctype.lower():
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="application/json required",
        )

async def _read_json(request: Request) -> Dict[str, Any]:
    try:
        return await request.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid JSON payload",
        )

@router.post("/echo")
async def submit_echo(request: Request):
    _require_json(request)
    payload = await _read_json(request)
    job_id = str(uuid4())
    JOBS[job_id] = {"status": "queued"}
    scheduler.add_job(_run_and_capture, id=job_id, replace_existing=True, args=[job_id, _echo_task, payload])
    return {"job_id": job_id}

@router.post("/kavach-scan")
async def submit_kavach(request: Request):
    _require_json(request)
    body = await _read_json(request)
    target = (body.get("target") or "127.0.0.1").strip()
    job_id = str(uuid4())
    JOBS[job_id] = {"status": "queued", "target": target}
    scheduler.add_job(_run_and_capture, id=job_id, replace_existing=True, args=[job_id, run_kavach_scan, target])
    return {"job_id": job_id}

@router.post("/trinetra-infer")
async def submit_trinetra(request: Request):
    _require_json(request)
    body = await _read_json(request)
    filename = (body.get("filename") or "qc_demo.csv").strip()
    job_id = str(uuid4())
    JOBS[job_id] = {"status": "queued", "filename": filename}
    scheduler.add_job(_run_and_capture, id=job_id, replace_existing=True, args=[job_id, run_trinetra_inference, filename])
    return {"job_id": job_id}

@router.get("/{job_id}")
def job_status(job_id: str):
    rec = JOBS.get(job_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    return {"job_id": job_id, **rec}