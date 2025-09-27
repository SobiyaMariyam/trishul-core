# app/api/jobs_api.py
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any
from uuid import uuid4
import threading
import time

# Import your actual job functions
from app.jobs import run_kavach_scan, run_trinetra_inference

router = APIRouter(prefix="/jobs", tags=["jobs"])

# ------------------------------------------------------------------
# In-memory job registry (thread-safe)
# ------------------------------------------------------------------
_JOBS: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()

def _new_job(payload: Dict[str, Any]) -> str:
    job_id = str(uuid4())
    with _LOCK:
        _JOBS[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "submitted_at": time.time(),
            "result": None,
            "payload": payload,
        }
    return job_id

def _set_status(job_id: str, status_: str, result: Any = None) -> None:
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id]["status"] = status_
            if result is not None:
                _JOBS[job_id]["result"] = result

def _get_job(job_id: str) -> Dict[str, Any]:
    with _LOCK:
        j = _JOBS.get(job_id)
        if not j:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
        return j

# ------------------------------------------------------------------
# Request models
# ------------------------------------------------------------------
class KavachScanReq(BaseModel):
    target: str = Field(..., description="Scan target (host/IP/domain)")

class TrinetraInferReq(BaseModel):
    filename: str = Field(..., description="Uploaded filename or path")

class EchoReq(BaseModel):
    message: str = Field(..., min_length=1)
    delay_seconds: float = Field(0, ge=0, le=30)

# ------------------------------------------------------------------
# Background runners (wrappers)
# ------------------------------------------------------------------
def _bg_kavach(job_id: str, req: KavachScanReq) -> None:
    try:
        _set_status(job_id, "running")
        result = run_kavach_scan(req.target)
        _set_status(job_id, "succeeded", result)
    except Exception as e:
        _set_status(job_id, "failed", {"error": str(e)})

def _bg_trinetra(job_id: str, req: TrinetraInferReq) -> None:
    try:
        _set_status(job_id, "running")
        result = run_trinetra_inference(req.filename)
        _set_status(job_id, "succeeded", result)
    except Exception as e:
        _set_status(job_id, "failed", {"error": str(e)})

def _bg_echo(job_id: str, req: EchoReq) -> None:
    try:
        _set_status(job_id, "running")
        if req.delay_seconds:
            time.sleep(float(req.delay_seconds))
        _set_status(job_id, "succeeded", {"echo": req.message, "processed_at": time.time()})
    except Exception as e:
        _set_status(job_id, "failed", {"error": str(e)})

# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@router.post("/kavach/scan")
def start_kavach_scan(req: KavachScanReq, bg: BackgroundTasks):
    """
    Start a Kavach scan as a background job.
    Returns a job_id you can poll at /jobs/status/{job_id}.
    """
    jid = _new_job({"module": "kavach", "target": req.target})
    bg.add_task(_bg_kavach, jid, req)
    return {"job_id": jid, "status": "queued"}

@router.post("/trinetra/infer")
def start_trinetra_inference(req: TrinetraInferReq, bg: BackgroundTasks):
    """
    Start a Trinetra inference as a background job.
    """
    jid = _new_job({"module": "trinetra", "filename": req.filename})
    bg.add_task(_bg_trinetra, jid, req)
    return {"job_id": jid, "status": "queued"}

@router.post("/echo")
def start_echo(req: EchoReq, bg: BackgroundTasks):
    """
    Small test job; useful to validate the background pipeline.
    """
    jid = _new_job({"module": "echo", "message": req.message, "delay": req.delay_seconds})
    bg.add_task(_bg_echo, jid, req)
    return {"job_id": jid, "status": "queued"}

@router.get("/status/{job_id}")
def job_status(job_id: str):
    """
    Check status/result for any job started by this API.
    """
    return _get_job(job_id)
