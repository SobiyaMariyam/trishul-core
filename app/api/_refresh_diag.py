from fastapi import APIRouter
from hashlib import sha256
import os

router = APIRouter(tags=["diag"])

ALG = os.getenv("ALGORITHM","HS256")
SECRET = os.getenv("SECRET_KEY","dev-secret-key")

@router.get("/auth/refresh/_diag")
def refresh_diag():
    try:
        from app.core.config import settings
        s2 = getattr(settings, "SECRET_KEY", None)
        a2 = getattr(settings, "ALGORITHM", None)
    except Exception:
        s2 = None; a2 = None
    return {
        "ALG_env": ALG,
        "SECRET_env_sha256": sha256(SECRET.encode()).hexdigest(),
        "ALG_settings": a2,
        "SECRET_settings_sha256": (sha256(s2.encode()).hexdigest() if isinstance(s2,str) else None),
    }
