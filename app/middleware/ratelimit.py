from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from starlette.responses import JSONResponse

# Configure limiter
limiter = Limiter(key_func=get_remote_address)

def init_rate_limit(app):
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": f"rate limit exceeded: {exc.detail}"},
        )
