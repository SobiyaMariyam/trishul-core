import logging, re, time, uuid, os
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

rid=ContextVar("rid", default="-"); tenant=ContextVar("tenant", default="-"); user=ContextVar("user", default="-")

class Ctx(logging.Filter):
    def filter(self, r):
        r.rid=rid.get("-"); r.tenant=tenant.get("-"); r.user=user.get("-")
        return True

def _install_record_factory():
    orig = logging.getLogRecordFactory()
    def factory(*args, **kwargs):
        rec = orig(*args, **kwargs)
        if not hasattr(rec, "rid"): rec.rid = rid.get("-")
        if not hasattr(rec, "tenant"): rec.tenant = tenant.get("-")
        if not hasattr(rec, "user"): rec.user = user.get("-")
        return rec
    logging.setLogRecordFactory(factory)

def _ensure_file_handler():
    try:
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "trishul.log")
        fmt = logging.Formatter("%(asctime)s %(levelname)s rid=%(rid)s tenant=%(tenant)s user=%(user)s %(message)s", "%Y-%m-%d %H:%M:%S")
        filt = Ctx()
        # if a handler already writes to trishul.log, reuse it; else add one
        root = logging.getLogger("")
        for h in root.handlers:
            if isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == os.path.abspath(log_path):
                h.setFormatter(fmt); h.addFilter(filt); return
        fh = RotatingFileHandler(log_path, maxBytes=10_000_000, backupCount=5, encoding="utf-8")
        fh.setFormatter(fmt); fh.addFilter(filt)
        root.addHandler(fh)
    except Exception:
        # Skip file logging in restrictive environments (CI, containers, etc.)
        pass

def setup_logging():
    try:
        _install_record_factory()
        _ensure_file_handler()
        # also make sure common loggers inherit the filter
        f=Ctx()
        for n in ("", "uvicorn", "uvicorn.error", "uvicorn.access"):
            try:
                lg=logging.getLogger(n); lg.setLevel(logging.INFO); lg.addFilter(f)
                for h in getattr(lg, "handlers", []): h.addFilter(f)
            except Exception:
                # Skip logger configuration if it fails
                pass
    except Exception:
        # Skip entire logging setup in restrictive environments
        pass

TENANT_RE=re.compile(r"^(?P<t>[^.]+)\.(?:lvh\.me|trishul\.cloud)(?::\d+)?$", re.I)
def parse_tenant(h):
    if not h: return "-"
    m=TENANT_RE.match(h.strip()); return m.group("t") if m else "-"

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req: Request, call_next):
        rid.set(req.headers.get("x-request-id") or str(uuid.uuid4()))
        tenant.set(parse_tenant(req.headers.get("host"))); user.set("-")
        t=time.perf_counter()
        logging.getLogger(__name__).info("request %s %s", req.method, req.url.path)
        try:
            resp: Response = await call_next(req)
        except Exception:
            logging.getLogger(__name__).exception("unhandled exception"); raise
        resp.headers["X-Request-ID"]=rid.get("-")
        logging.getLogger(__name__).info(
            "response %s %s -> %s in %dms",
            req.method, req.url.path, resp.status_code, int((time.perf_counter()-t)*1000)
        )
        return resp
