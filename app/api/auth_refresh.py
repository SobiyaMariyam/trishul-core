# app/api/auth_refresh.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Any

import os
from fastapi import APIRouter, Header, HTTPException, Request, status
from jose import jwt, JWTError

router = APIRouter(tags=["auth"])

# Use the same settings your app already relies on
ALG = os.getenv("ALGORITHM", "HS256")
SECRET = os.getenv("SECRET_KEY", "dev-secret-key")
LEEWAY_SECONDS = int(os.getenv("JWT_LEEWAY", "60"))  # tolerate small clock skew


def _decode(token: str, expected_aud: Optional[str]) -> dict:
    """
    Decode WITHOUT built-in audience verification, then enforce audience manually.
    This avoids python-jose's strict audience list typing issues.
    Also applies a small leeway for exp/nbf to tolerate clock skew.
    """
    try:
        claims = jwt.decode(
            token,
            SECRET,
            algorithms=[ALG],
            options={
                "verify_aud": False,     # we'll check 'aud' ourselves
                "leeway": LEEWAY_SECONDS # tolerate small skew on exp/nbf
            },
        )
    except JWTError as e:
        # Include jose's message so callers see 'Signature has expired', etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token: {e}"
        )

    # Manual audience enforcement (case-insensitive)
    if expected_aud:
        aud_val: Any = claims.get("aud")
        aud_list = aud_val if isinstance(aud_val, (list, tuple)) else [aud_val]
        ok = any(
            isinstance(a, str) and a.lower() == expected_aud.lower()
            for a in aud_list
            if a is not None
        )
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token: Invalid audience",
            )

    return claims


@router.post("/auth/refresh")
def refresh_token(request: Request, authorization: Optional[str] = Header(None)):
    """
    Exchange a valid (not too-expired) bearer token for a fresh 15-minute token.
    Enforces per-tenant audience and (if present) tenant-id claim consistency.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing token",
        )

    token = authorization.split(" ", 1)[1].strip()
    path_tenant: Optional[str] = getattr(request.state, "tenant", None)

    # Decode + validate audience manually
    old = _decode(token, expected_aud=path_tenant)

    # Enforce tenant-id consistency when present
    tid = (old.get("tid") or old.get("tenant_id") or "").strip()
    if path_tenant and tid and tid.lower() != path_tenant.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token tenant mismatch",
        )

    # Build new short-lived access token (15 minutes)
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