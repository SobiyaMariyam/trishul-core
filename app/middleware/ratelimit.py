from slowapi import Limiter
from slowapi.util import get_remote_address

def _key_func(request):
    # Per-tenant + IP key (so each tenant/IP combo has its own bucket)
    tenant = getattr(getattr(request, "state", None), "tenant", "unknown")
    ip = get_remote_address(request) or "noip"
    return f"{tenant}:{ip}"

# Add a small default to demonstrate 429s; tune later
limiter = Limiter(
    key_func=_key_func,
    default_limits=["10/minute"],   # <-- new default limit
)

def init_rate_limit(app):
    app.state.limiter = limiter