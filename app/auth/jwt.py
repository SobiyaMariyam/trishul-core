from datetime import datetime, timedelta, timezone
import os
from typing import Any, Dict, Optional

import jwt  # PyJWT

ALGORITHM = "HS256"

def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        # Safe default for dev; rotate in 2.2
        secret = "dev-secret"
    return secret

def create_access_token(
    subject: str,
    tenant: str,
    role: str,
    expires_minutes: int = 60,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a short-lived access token.
    Required claims: sub, tid (tenant), role, exp, iat
    """
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "tid": tenant,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)
    # PyJWT returns str on modern versions
    return token

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate the JWT. Raises jwt exceptions on invalid tokens.
    Ensures required claims exist.
    """
    claims = jwt.decode(token, _get_secret(), algorithms=[ALGORITHM])
    for required in ("sub", "tid", "role", "exp"):
        if required not in claims:
            raise jwt.InvalidTokenError(f"missing claim: {required}")
    return claims
