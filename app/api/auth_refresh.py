from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Header, HTTPException, status, Request
from jose import jwt, JWTError
import os
from typing import Optional, Any

router = APIRouter(tags=["auth"])

ALG = os.getenv("ALGORITHM", "HS256")
SECRET = os.getenv("SECRET_KEY", "dev-secret-key")

def _decode(token: str, expected_aud: Optional[str]) -> dict:
    """
    Decode WITHOUT audience verification, then enforce audience manually.
    This avoids python-jose's strict audience type rules.
    """
    try:
        claims = jwt.decode(
            token,
            SECRET,
            algorithms=[ALG],
            options={"verify_aud": False}  # we'll check 'aud' ourselves
        )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid token: {e}")

    if expected_aud:
        aud_val: Any = claims.get("aud")
        aud_list = aud_val if isinstance(aud_val, (list, tuple)) else [aud_val]
        ok = any((isinstance(a, str) and a.lower() == expected_aud.lower()) for a in aud_list if a is not None)
        if not ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token: Invalid audience")
    return claims

@router.post("/auth/refresh")
def refresh_token(request: Request, authorization: str | None = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")

    token = authorization.split(" ", 1)[1].strip()
    path_tenant: Optional[str] = getattr(request.state, "tenant", None)

    old = _decode(token, expected_aud=path_tenant)

    # Enforce tenant match if tid present
    tid = (old.get("tid") or old.get("tenant_id") or "").strip().lower()
    if path_tenant and tid and tid != path_tenant.lower():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token tenant mismatch")

    now = datetime.now(timezone.utc)
    new_claims = {
        "sub": old.get("sub"),
        "tid": tid or (path_tenant or ""),
        "role": old.get("role"),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
        "aud": (old.get("aud") or tid or (path_tenant or "")),
    }
    return {
        "access_token": jwt.encode(new_claims, SECRET, algorithm=ALG),
        "token_type": "bearer",
        "expires_in": 900,
    }
