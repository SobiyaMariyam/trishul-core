import logging, re, time, uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

rid=ContextVar("rid", default="-"); tenant=ContextVar("tenant", default="-"); user=ContextVar("user", default="-")

class Ctx(logging.Filter):
    def filter(self, r): r.rid=rid.get("-"); r.tenant=tenant.get("-"); r.user=user.get("-"); return True

def setup_logging():
    f=Ctx()
    for n in ("", "uvicorn", "uvicorn.error", "uvicorn.access"):
        lg=logging.getLogger(n); lg.setLevel(logging.INFO); lg.addFilter(f)
        for h in lg.handlers: h.addFilter(f)

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
        logging.getLogger(__name__).info("response %s %s -> %s in %dms",
            req.method, req.url.path, resp.status_code, int((time.perf_counter()-t)*1000))
        return resp
