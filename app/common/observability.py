import uuid
import logging, os
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Context: request id for log records
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

# Single logger for the app
_LOGGER = None
def get_logger():
    global _LOGGER
    if _LOGGER:
        return _LOGGER
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("trishul")
    logger.setLevel(logging.INFO)
    h = RotatingFileHandler("logs/trishul.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    f = logging.Formatter("%(asctime)s %(levelname)s rid=%(request_id)s tenant=%(tenant)s user=%(user)s %(message)s")
    h.setFormatter(f)
    class Ctx(logging.Filter):
        def filter(self, record):
            try:
                record.request_id = request_id_ctx.get()
            except Exception:
                record.request_id = "-"
            if not hasattr(record, "tenant"): record.tenant = "-"
            if not hasattr(record, "user"):   record.user   = "-"
            return True
    logger.addHandler(h)
    logger.addFilter(Ctx())
    _LOGGER = logger
    return logger

class RequestAuditMiddleware(BaseHTTPMiddleware):
    """Adds X-Request-ID and writes one audit line per request."""
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger()

    async def dispatch(self, request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        tok = request_id_ctx.set(rid)
        tenant = (getattr(getattr(request, "state", None), "tenant", None) or request.headers.get("Host","default")).split(".")[0]
        user   = getattr(getattr(request, "state", None), "user", "-")
        try:
            response = await call_next(request)
            status = getattr(response, "status_code", 200)
        except Exception:
            status = 500
            self.logger.exception("unhandled error", extra={"tenant": tenant, "user": user})
            request_id_ctx.reset(tok)
            raise
        request_id_ctx.reset(tok)
        # audit line
        self.logger.info("request %s %s -> %s", request.method, request.url.path, status,
                         extra={"tenant": tenant, "user": user})
        # echo header
        response.headers["X-Request-ID"] = rid
        return response
