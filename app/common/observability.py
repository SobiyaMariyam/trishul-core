from __future__ import annotations
import json, logging, os, re, time, uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# -------------------------------
# Correlation / context variables
# -------------------------------
RID     = ContextVar("rid", default="-")
TENANT  = ContextVar("tenant", default="-")
ACTOR   = ContextVar("actor", default="-")

# -------------------------------
# Redaction rules (tokens, PII)
# -------------------------------
_REDACTIONS = [
    (re.compile(r"(?i)(authorization:\s*Bearer\s+)[A-Za-z0-9\-\._]+"), r"\1[REDACTED]"),
    (re.compile(r'(?i)("secret(_?key)?"\s*:\s*")[^"]+(")'), r'\1[REDACTED]\3'),
    (re.compile(r'(?i)("password"\s*:\s*")[^"]+(")'), r'\1[REDACTED]\2'),
    (re.compile(r'(?i)(api[_\-]?key)\s*[:=]\s*([A-Za-z0-9\-_]+)'), r'\1=[REDACTED]'),
    (re.compile(r'(?i)("email"\s*:\s*")[^"]+(")'), r'\1[REDACTED]\2'),
]

def _redact(s: str) -> str:
    out = s
    for rx, repl in _REDACTIONS:
        out = rx.sub(repl, out)
    return out

# -------------------------------
# Tenant inference from Host
# -------------------------------
TENANT_RE = re.compile(r"^(?P<t>[^.:]+)\.(?:lvh\.me|trishul\.cloud)(?::\d+)?$", re.I)

def parse_tenant_from_host(host: str | None) -> str:
    if not host:
        return "-"
    m = TENANT_RE.match(host.strip())
    return m.group("t") if m else "-"

# -------------------------------
# Structured JSON logging
# -------------------------------
LOG_DIR  = os.path.abspath(os.getenv("LOG_DIR", "logs"))
LOG_PATH = os.path.join(LOG_DIR, "app.log")

class AppendOnlyFileHandler(logging.FileHandler):
    """Append-only file handler (no truncation/rotation)."""
    def _open(self):
        os.makedirs(os.path.dirname(self.baseFilename), exist_ok=True)
        return open(self.baseFilename, mode="a", encoding=self.encoding, errors=self.errors)

class CtxFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Ensure context fields exist on record
        record.rid    = RID.get("-")
        record.tenant = TENANT.get("-")
        record.actor  = ACTOR.get("-")
        return True

def _install_record_factory() -> None:
    orig = logging.getLogRecordFactory()
    def factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        rec = orig(*args, **kwargs)
        if not hasattr(rec, "rid"):    rec.rid    = RID.get("-")
        if not hasattr(rec, "tenant"): rec.tenant = TENANT.get("-")
        if not hasattr(rec, "actor"):  rec.actor  = ACTOR.get("-")
        return rec
    logging.setLogRecordFactory(factory)

def setup_logging() -> None:
    """Idempotent global logger setup with JSON-ish, append-only logs."""
    root = logging.getLogger()
    if root.handlers:
        # Already configured
        return

    _install_record_factory()

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    root.setLevel(getattr(logging, level, logging.INFO))

    # Simple line format for human tail + full JSON in message field
    line_fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s rid=%(rid)s tenant=%(tenant)s actor=%(actor)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    ctx_filter = CtxFilter()

    fh = AppendOnlyFileHandler(LOG_PATH, encoding="utf-8")
    fh.setLevel(root.level)
    fh.setFormatter(line_fmt)
    fh.addFilter(ctx_filter)
    root.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(root.level)
    sh.setFormatter(line_fmt)
    sh.addFilter(ctx_filter)
    root.addHandler(sh)

    # Propagate filter to common loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.setLevel(root.level)
        lg.addFilter(ctx_filter)
        for h in lg.handlers:
            h.addFilter(ctx_filter)

# -------------------------------
# Middleware
# -------------------------------
class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    - Creates/propagates a correlation ID (X-Request-ID)
    - Infers tenant (request.state.tenant or Host) and actor (request.state.actor)
    - Logs structured JSON audit records (request + response)
    - Redacts sensitive tokens
    """

    async def dispatch(self, request: Request, call_next):
        # Correlation ID
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        RID.set(rid)

        # Tenant: prefer what an earlier tenancy middleware put on state; else from Host
        tenant = getattr(getattr(request, "state", None), "tenant", None) or parse_tenant_from_host(request.headers.get("host"))
        TENANT.set(tenant if tenant else "-")

        # Actor: prefer state.actor (e.g., set by auth middleware)
        actor = getattr(getattr(request, "state", None), "actor", None) or "-"
        ACTOR.set(actor)

        # Prepare request summary (don’t read body to avoid memory & privacy)
        req_meta = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "rid": rid,
            "tenant": TENANT.get("-"),
            "actor": ACTOR.get("-"),
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) if request.query_params else "",
            "stage": "request",
        }
        logging.info(_redact(json.dumps(req_meta, separators=(",", ":"), ensure_ascii=False)))

        t0 = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception as e:
            # Log exception with correlation id
            err_meta = {
                **req_meta,
                "stage": "error",
                "error": str(e.__class__.__name__),
            }
            logging.exception(_redact(json.dumps(err_meta, separators=(",", ":"), ensure_ascii=False)))
            raise

        # Duration & response
        ms = int((time.perf_counter() - t0) * 1000)
        try:
            response.headers["X-Request-ID"] = rid
        except Exception:
            pass

        resp_meta = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "rid": rid,
            "tenant": TENANT.get("-"),
            "actor": ACTOR.get("-"),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": ms,
            "stage": "response",
        }
        logging.info(_redact(json.dumps(resp_meta, separators=(",", ":"), ensure_ascii=False)))
        return response